import asyncio
import os
import json
import config     
import setup  

async def run_pipeline():
   
    num_stories = 16 
    for i in range(num_stories):
        
        # Ensure variety across 16 stories 
        main_idx = i % len(config.characters)
        sub_idx = (i + 2) % len(config.characters)  
        loc_idx = i % len(config.locations)
        
        # Ensure main and sub char are different
        if main_idx == sub_idx:
            sub_idx = (sub_idx + 1) % len(config.characters)
        
        main_char = config.characters[main_idx]
        sub_char = config.characters[sub_idx]
        location = config.locations[loc_idx]
        
        # Unity-friendly folder structure
        story_id = f"story_{i+1:02d}"
        story_folder = os.path.join(config.output_dir, story_id)
        os.makedirs(story_folder, exist_ok=True)
        
        final_json_path = os.path.join(story_folder, "story_data.json")
        if os.path.exists(final_json_path):
            print(f"Skipping {story_id} (Already complete)")
            continue
        
        print(f"STARTING STORY {i+1}/{num_stories}: {story_id}")
        print(f"Main: {main_char['name']}")
        print(f"Supporting: {sub_char['name']}")
        print(f"Location: {location['name']} - {location['description']}")

        full_story = {
            "storyId": story_id,
            "title": f"{main_char['short_name']}'s Adventure in {location['name']}",
            "mainCharacter": main_char['name'],
            "supportingCharacter": sub_char['name'],
            "location": location['name'],
            "pages": [] 
        }

        page_global_counter = 0

        # Process each of the 6 story parts
        for part_idx, part in enumerate(config.story_structure):
            print(f"\nPart {part_idx + 1}/6: {part}")
            
            plan_prompt = f"""
                [PERSONA]
                You are a Lead Narrative Designer for a top-tier kids' game studio (Age 5-8).

                [CONTEXT]
                Story Part: {part}
                World Setting: {config.background}
                Main Character: {main_char['name']}
                - Role: {main_char['role']}
                - Personality: {main_char['traits']}
                Supporting Character: {sub_char['name']} - {sub_char['role']}
                Location: {location['name']} - {location['description']}

                [TASK]
                Create a detailed story plan for this part.

                [CHAIN OF THOUGHT]
                Think step-by-step:
                1. What specific event happens in {part} that advances the story?
                2. How does {main_char['short_name']}'s trait help or hinder them?
                3. What role does {sub_char['short_name']} play?
                4. How does {location['name']} setting enhance the scene?
                5. What is the logical sequence that makes sense for 5-8 year olds?

                [OUTPUT FORMAT - STRICT JSON]
                {{
                    "reasoning": "Your detailed chain-of-thought reasoning (2-4 sentences explaining the logic)",
                    "plan": {{
                        "Details": "Rich sensory description of scene, mood, atmosphere. Paint a vivid picture. (3-4 sentences)",
                        "Overcome": "Specific problem and how character solves it using their traits. Clear action. (2-3 sentences)",
                        "SequenceEvents": "Step-by-step breakdown: First... Then... Next... Finally... (4-5 clear sequential steps)"
                    }}
                }}

                [EXAMPLE FOR SETUP PART]
                {{
                    "reasoning": "In Setup, Alice arrives at Melody Grove full of curiosity. She meets Jungle Boy who is exploring the singing trees. The grove's magical nature sets up the adventure.",
                    "plan": {{
                        "Details": "Melody Grove sparkles in morning sunlight. Ancient trees sway and hum gentle melodies. Musical notes float through the air like fireflies. Alice stands at the entrance, eyes wide with wonder, while Jungle Boy climbs a nearby tree.",
                        "Overcome": "Alice wants to understand the trees' songs. She uses her notebook to record patterns while Jungle Boy helps identify which trees sing the loudest.",
                        "SequenceEvents": "First, Alice enters the grove with her notebook ready. Then, she spots Jungle Boy in a tree. Next, Jungle Boy shows her the singing trees. After that, Alice begins recording the melodies. Finally, they discover the trees sing different songs based on the wind."
                    }}
                }}

                Generate the plan for {part} now.
                """
            plan_data = setup.generate_json(plan_prompt, f"📝 Planning: {part}")
            
            # Validate and provide fallback if needed
            if "plan" not in plan_data or plan_data.get("fallback"):
                print(f"⚠️ Plan generation had issues, using fallback")
                plan_data = {
                    "reasoning": f"Fallback plan for {part}",
                    "plan": {
                        "Details": f"{main_char['short_name']} explores {location['name']} with {sub_char['short_name']}",
                        "Overcome": f"{main_char['short_name']} faces a challenge and solves it",
                        "SequenceEvents": "First, they arrive. Then, they discover something. Next, they take action. Finally, they succeed."
                    }
                }

            draft_prompt = f"""
                [PERSONA]
                You are a Children's Book Author (Ages 5-8).
                Style: Whimsical, Simple, Warm, Engaging, Positive.

                [INPUT DATA]
                Story Plan for {part}:
                {json.dumps(plan_data['plan'], indent=2)}

                Characters: {main_char['short_name']} and {sub_char['short_name']}
                Location: {location['name']}

                [TASK]
                Write the story text for this part, divided into EXACTLY 3 pages.

                [CONSTRAINTS]
                - EXACTLY 3 pages, no more, no less
                - Each page: 2-4 short, simple sentences
                - Vocabulary: 5-year-old to 8-year-old reading level (short words, simple concepts)
                - Include sensory details (what they see, hear, feel)
                - Both characters should be present or mentioned
                - Positive, encouraging tone
                - Each page flows naturally to the next

                [OUTPUT FORMAT - STRICT JSON]
                {{
                    "pages": [
                        "Page 1 text: 2-4 simple sentences opening this part...",
                        "Page 2 text: 2-4 simple sentences continuing the action...",
                        "Page 3 text: 2-4 simple sentences concluding this part..."
                    ]
                }}

                [EXAMPLE FOR SETUP]
                {{
                    "pages": [
                        "{main_char['short_name']} walked into {location['name']}, eyes sparkling with wonder. The trees hummed a gentle welcome song. {sub_char['short_name']} waved from a nearby branch.",
                        "{main_char['short_name']} pulled out her special notebook. 'What a curious delight!' she said with a smile. {sub_char['short_name']} climbed down to help her.",
                        "Together they listened to the magical trees. Each tree sang a different tune. This was going to be a wonderful adventure!"
                    ]
                }}

                Generate the 3 pages for {part} now.
                """
            draft_data = setup.generate_json(draft_prompt, f"✍️ Drafting: {part}")
            
            # Validate draft
            if "pages" not in draft_data or len(draft_data.get("pages", [])) != 3:
                print(f"Draft generation had issues, using fallback")
                draft_data = {"pages": [
                    f"{main_char['short_name']} and {sub_char['short_name']} began their adventure in {location['name']}.",
                    f"Something magical happened. They worked together to solve it.",
                    f"They smiled at each other. This was going to be fun!"
                ]}

            # Refine + generate assets
            for page_idx, raw_text in enumerate(draft_data['pages']):
                page_num_in_part = page_idx + 1
                print(f"\n  📄 Page {page_num_in_part}/3 of {part}")
                
                # REFINE THE TEXT
                refine_prompt = f"""
                    [ROLE]
                    You are a Children's Book Content Editor (Ages 5-8). Your job is to ensure safety and quality .

                    [INPUT TEXT]
                    "{raw_text}"

                    [CHARACTER CONTEXT]
                    Main: {main_char['short_name']} - {main_char['traits']}
                    Supporting: {sub_char['short_name']} - {sub_char['traits']}
                    Location: {location['name']}

                    [EVALUATION CRITERIA]
                    1. Age-Appropriateness:
                    - USE simple vocabulary that a 5-year-old can understand
                    - KEEP Short, clear sentences
                    - MAINTAIN a positive, encouraging tone
                    - MAKE it engaging and fun
                    - USE a simple narration style for children to understand

                    2. Consistency:
                    - Matches {main_char['short_name']}'s personality and traits?
                    - Fits the {location['name']} setting?
                    - Flows logically?
                    - Follow the story plan and story structure?

                    3. Safety & Quality:
                    - NO scary or negative themes
                    - REMOVE any inappropriate content related to violence, fear, or adult topics
                    - MAKE it wholesome and uplifting
                    - FIX all grammar and punctuation errors
    

                    [TASK]
                    Improve the text to meet all criteria. Keep it around the same length (2-4 sentences).

                    [OUTPUT FORMAT - STRICT JSON]
                    {{
                        "critique": "Brief note on what you improved or kept (1-2 sentences)",
                        "final_text": "The polished, perfect text (2-4 sentences)"
                    }}

                    Refine now.
                    """
                refined_data = setup.generate_json(
                    refine_prompt, 
                    f"  ✨ Refining Page {page_num_in_part}"
                )
                
                # Validate refinement
                if "final_text" not in refined_data:
                    refined_data = {
                        "critique": "Used original text as-is",
                        "final_text": raw_text
                    }
                
                # GENERATE IMAGE PROMPT
                img_prompt_req = f"""
                    [TASK]
                    Describe the PHYSICAL ACTION and POSE for an AI image generator.
                    
                    [STORY TEXT]
                    "{refined_data['final_text']}"

                    [CHARACTERS]
                    1. {main_char['short_name']}
                    2. {sub_char['short_name']}
                    
                    [LOCATION]
                    {location['name']}

                    [STRICT RULES - TO PREVENT GLITCHES]
                    1. Describe ONLY the action (sitting, running, pointing) and facial expression (smiling, surprised).
                    2. DO NOT describe clothes, hair color, or accessories (These are handled automatically).
                    3. DO NOT mention "art style" or "illustration".
                    4. KEEP CHARACTERS SEPARATE if possible (e.g., "Alice stands on left, Jungle Boy sits on right").
                    5. AVOID complex interactions like "holding hands" or "hugging".
                    6. Max 2 short sentences.

                    [OUTPUT FORMAT - STRICT JSON]
                    {{
                        "image_prompt": "Alice standing on a rock pointing at a tree. Jungle Boy sitting on a branch looking down smiling."
                    }}

                    Generate image prompt now.
                    """
                img_data = setup.generate_json(img_prompt_req,  f"Image Prompt Page {page_num_in_part}")
                
                # Validate image prompt
                if "image_prompt" not in img_data:
                    img_data = {
                        "image_prompt": f"{main_char['short_name']} and {sub_char['short_name']} in {location['name']}, {location['description']}"
                    }
                
                # GENERATE IMAGE AND AUDIO FILES
                img_filename = f"page_{page_global_counter:02d}.png"
                audio_filename = f"page_{page_global_counter:02d}.mp3"
                img_path = os.path.join(story_folder, img_filename)
                audio_path = os.path.join(story_folder, audio_filename)
                
                if os.path.exists(img_path):
                    print(f"Skipping Image {page_global_counter} (Exists)")
                else:
                    print(f"Generating: {img_filename}")
                    setup.generate_image(
                        scene_description=img_data['image_prompt'],
                        filepath=img_path,
                        main_char_dict=main_char,
                        sub_char_dict=sub_char,
                        location_dict=location
                    )
                
                if os.path.exists(audio_path):
                    print(f"Skipping Audio {page_global_counter} (Exists)")
                else:
                    print(f"Generating: {audio_filename}")
                    await setup.generate_audio(refined_data['final_text'], audio_path)

                # STORE PAGE DATA
                full_story['pages'].append({
                    "pageNumber": page_global_counter,
                    "partName": part,
                    "storyText": refined_data['final_text'],
                    "imageFileName": img_filename,
                    "audioFileName": audio_filename,
                    "planReasoning": plan_data.get('reasoning', ''),
                    "imagePrompt": img_data['image_prompt'],
                    "editorCritique": refined_data.get('critique', '')
                })
                
                page_global_counter += 1
                print(f"Page {page_global_counter} complete")

        # SAVE COMPLETE STORY JSON
        json_path = os.path.join(story_folder, "story_data.json")
        with open(json_path, "w", encoding='utf-8') as f:
            json.dump(full_story, f, indent=4, ensure_ascii=False)
        
        print(f"{story_id} COMPLETE!")
        print(f"Saved to: {json_path}")
        print(f"Total Pages: {len(full_story['pages'])}")
        print(f"Expected: 18 pages (6 parts × 3 pages)")

    print(f"ALL {num_stories} STORIES GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_pipeline())