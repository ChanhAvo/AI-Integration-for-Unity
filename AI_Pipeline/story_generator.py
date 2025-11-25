"""
Merged plan + draft + refine pipeline per story.
Function: generate_story(story_id, main_char, sub_char, location)
Writes story folder with pages and returns story dict.
"""

import os
import json
import time
import asyncio
from typing import Dict

import config
import prompts
import setup


def count_words(text: str) -> int:
    return len([w for w in text.split() if w.strip()])

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


def generate_story(story_id: str, main: Dict, sub: Dict, location: Dict, out_root: str):

    story_folder = os.path.join(out_root, story_id)
    os.makedirs(story_folder, exist_ok=True)

    story = {
        "storyId": story_id,
        "title": f"{main['short_name']}'s Adventure in {location['name']}",
        "characters": [main["name"], sub["name"]],
        "location": location["name"],
        "pages": []
    }

    prev_summary = "The story begins."
    page_counter = 0

    for part in config.story_structure:


        # Plan
       
        plan_prompt = render_plan_prompt(part, main, sub, location, prev_summary)
        plan_name = f"{story_id}_{part}_plan_{int(time.time())}"
        setup.log_prompt(plan_name, plan_prompt)
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
            setup.log_prompt(draft_name, draft_prompt)
            draft_resp = setup.call_llm(draft_prompt, draft_name)

            pages = draft_resp.get("pages")

            if not pages or len(pages) != 3:
                continue

            # Check each page's word count
            word_counts = [count_words(p) for p in pages]
            if all(30 <= wc <= 40 for wc in word_counts):
                total_words = sum(word_counts)
                if 90 <= total_words <= 120:
                    accepted_pages = pages
                    break

            print(f"[WordCheck] '{part}' failed word rules {word_counts}. Regenerating...")

        # Fallback
        if accepted_pages is None:
            accepted_pages = pages

    
        for page_text in accepted_pages:

            # Refine
            refine_prompt = render_refine_prompt(page_text, main, sub, location)
            refine_name = f"{story_id}_refine_{page_counter}_{int(time.time())}"
            setup.log_prompt(refine_name, refine_prompt)
            refine_resp = setup.call_llm(refine_prompt, refine_name)

            final_text = refine_resp.get("final_text", page_text)

            # Image request
            imgreq_prompt = render_image_request(final_text, main, sub, location)
            imgreq_name = f"{story_id}_imgreq_{page_counter}_{int(time.time())}"
            setup.log_prompt(imgreq_name, imgreq_prompt)
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
                asyncio.run(setup.generate_audio(final_text, audio_path))
            except Exception:
                pass

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

            page_counter += 1

    # Save story
    with open(os.path.join(story_folder, "story_data.json"), "w", encoding="utf-8") as f:
        json.dump(story, f, ensure_ascii=False, indent=2)

    return story
