import os
import json
import time
import asyncio
from typing import Dict

import config
import prompts
import setup

def save_story_json(story_folder, story_data):
    path = os.path.join(story_folder, "story_data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(story_data, f, ensure_ascii=False, indent=2)

def render_plan_prompt(part, main, sub, location, prev_summary):
    return prompts.PLAN_PROMPT.format(
        part=part,
        background=config.background,
        main_name=main["name"],
        main_role=main["role"],
        main_traits=main["traits"],
        sub_name=sub["name"],
        sub_role=sub["role"],
        sub_traits=sub["traits"],
        location_name=location["name"],
        location_desc=location["description"],
        prev_summary=prev_summary
    )


def render_draft_prompt(plan_json, main, sub, location):
    return prompts.DRAFT_PROMPT.format(
        plan_json=json.dumps(plan_json, ensure_ascii=False),
        main_short=main["short_name"],
        sub_short=sub["short_name"],
        main_traits=main["traits"],
        sub_traits=sub["traits"],
        location_name=location["name"]
    )


def render_refine_prompt(raw_text, main, sub, location):
    return prompts.REFINE_PROMPT.format(
        raw_text=raw_text,
        main_short=main["short_name"],
        main_traits=main["traits"],
        sub_short=sub["short_name"],
        sub_traits=sub["traits"],
        location_name=location["name"]
    )


def render_image_request(text, main, sub, location):
    return prompts.IMAGE_PROMPT.format(
        page_text=text.replace('"', "'"),
        location_name=location["name"],
        location_desc=location["description"],
        main_blueprint=json.dumps(config.char_bp.get(main["short_name"], {}), ensure_ascii=False),
        sub_blueprint=json.dumps(config.char_bp.get(sub["short_name"], {}), ensure_ascii=False),
        global_style=json.dumps(config.global_style, ensure_ascii=False)
        if isinstance(config.global_style, dict)
        else config.global_style,
        negative=config.negative_prompt
    )


async def generate_story(story_id: str, main: Dict, sub: Dict, location: Dict, out_root: str):

    story_folder = os.path.join(out_root, story_id)
    os.makedirs(story_folder, exist_ok=True)

    story = {
        "storyId": story_id,
        "title": f"{main['short_name']}'s Adventure in {location['name']}",
        "characters": [main["name"], sub["name"]],
        "location": location["name"],
        "pages": []
    }
    
    save_story_json(story_folder, story)
    
    prev_summary = "The story begins."
    page_counter = 0

    for part in config.story_structure:


        # Plan
        plan_prompt = render_plan_prompt(part, main, sub, location, prev_summary)
        plan_name = f"{story_id}_{part}_plan_{int(time.time())}"
        plan_resp = setup.call_llm(plan_prompt, plan_name)

        if plan_resp.get("fallback") or "plan" not in plan_resp:
            plan = {
                "Details": f"{main['short_name']} explores {location['name']}.",
                "Overcome": f"{main['short_name']} tries something clever.",
                "SequenceEvents": "First... | Then... | Next... | Finally..."
            }
        else:
            plan = plan_resp["plan"]

        prev_summary = plan.get("Overcome", prev_summary)

        # Draft
        
        accepted_pages = None
        for attempt in range(6): 
            draft_prompt = render_draft_prompt(plan, main, sub, location)
            draft_name = f"{story_id}_{part}_draft_{int(time.time())}"
            
            # Call LLM
            draft_resp = setup.call_llm(draft_prompt, draft_name)
            pages = draft_resp.get("pages")
            if pages and isinstance(pages, list) and len(pages) == 3:
                accepted_pages = pages
                print(f"   [Draft] Success on attempt {attempt+1}")
                break 
            
            print(f"   [Draft] Attempt {attempt+1} failed validation. Retrying...")

        # FALLBACK LOGIC
        if accepted_pages is None:
            print(f"   [Draft] CRITICAL: All 6 attempts failed. Using placeholders.")
            accepted_pages = [
                f"The story continued in {location['name']}...",
                "Something unexpected happened...", 
                "And they moved on to the next adventure."
            ]

    
        for page_text in accepted_pages:

            # Refine
            refine_prompt = render_refine_prompt(page_text, main, sub, location)
            refine_name = f"{story_id}_refine_{page_counter}_{int(time.time())}"
            refine_resp = setup.call_llm(refine_prompt, refine_name)

            final_text = refine_resp.get("final_text", page_text)

            # Image request
            imgreq_prompt = render_image_request(final_text, main, sub, location)
            imgreq_name = f"{story_id}_imgreq_{page_counter}_{int(time.time())}"
            imgreq_resp = setup.call_llm(imgreq_prompt, imgreq_name)

            bg = imgreq_resp.get("bg_details", location["description"])
            action = imgreq_resp.get("action", f"{main['short_name']} and {sub['short_name']} together")

            main_blue = config.char_bp.get(main["short_name"], {})
            sub_blue = config.char_bp.get(sub["short_name"], {})
            loc_blue = config.loc_bp.get(location["name"], {})

            sd_prompt = (
                f"{config.global_style['art_style']}. "
                f"SCENE: {bg}. "
                f"ACTION: {action}. "
                f"CHARACTER_HINTS: {main_blue.get('always_include','')}; "
                f"SUPPORT_HINTS: {sub_blue.get('always_include','')}. "
                f"ENV_HINTS: {loc_blue.get('always_include','')}. "
                f"Whimsical children's book illustration, highly detailed."
            )

            # Image generation
            combined_seed = (
                main.get("seed", 0)
                + sub.get("seed", 0)
                + location.get("seed", 0)
                + page_counter
            ) % 2147483647

            img_name = f"page_{page_counter:03d}.png"
            img_path = os.path.join(story_folder, img_name)

            sd_res = setup.generate_image(
                sd_prompt,
                config.negative_prompt,
                combined_seed,
                img_path,
                model_name=config.image_model
            )

            # Audio
            audio_name = f"page_{page_counter:03d}.mp3"
            audio_path = os.path.join(story_folder, audio_name)
            try:
                await setup.generate_audio(final_text, audio_path)
            except Exception as e:
                print(f"Audio failed for page {page_counter}: {e}")

            # Save page
            story["pages"].append({
                "pageNumber": page_counter,
                "part": part,
                "text": final_text,
                "imageFileName": img_name,
                "audioFileName": audio_name,
                "plan": plan,
                "img_request": imgreq_resp,
                "sd_prompt": sd_prompt,
                "sd_result": sd_res
            })
            
            save_story_json(story_folder, story)
            print(f"Saved Page {page_counter} of Story {story_id}")
            page_counter += 1
    return story