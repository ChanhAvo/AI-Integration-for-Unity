import asyncio
import os
import json
import config     
import setup  

async def run_pipeline():
    for i in range(1): 
        
        #Set up structure
        main_char = config.characters[i % len(config.characters)]
        sub_char = config.characters[(i + 1) % len(config.characters)]
        loc = config.locations[i % len(config.locations)]
        
        # Unity-friendly Folder Structure
        story_id = f"story_{i+1:02d}"
        story_folder = os.path.join(config.output_dir, story_id)
        os.makedirs(story_folder, exist_ok=True)
        
        print(f"\n Starting {story_id}: {main_char['name']} in {loc} ===")

    
        full_story = {
            "storyId": story_id,
            "title": f"{main_char['name']} and the Adventure in {loc}",
            "pages": [] 
        }

        page_global_counter = 0

        # Process story part
        for part in config.STORY_STRUCTURE:
            print(f"\nProcessing Part: {part} ")
            
            #Story plan
            plan_prompt = f"""
            [PERSONA]
            You are a Lead Narrative Designer for a top-tier kids' game (Age 5-8).
            
            [CONTEXT]
            Part: {part}
            World Context: {config.background}
            Characters: {main_char['name']} ({main_char['traits']}) & {sub_char['name']}.
            Location: {loc}
            
            [TASK]
            Create a story plan. 
            
            [CHAIN OF THOUGHT INSTRUCTION]
            First, think logically:
            1. What is the specific goal of this scene?
            2. How does {main_char['name']}'s specific trait ({main_char['traits']}) solve the problem?
            3. What is the step-by-step physical action?
            
            [OUTPUT FORMAT]
            Return ONLY JSON:
            {{
                "reasoning": "Your chain of thought here...",
                "plan": {{
                    "Details": "Paints the scene and sets the mood, for example descriptive elements for immersion",
                    "Overcome": "Shows how characters solve a problem, for example key actions or decisions",
                    "SequenceEvents": "Organizes the action clearly, and step-by-step events"
                }}
            }}
            """
            plan_data = setup.generate_json(plan_prompt, "Step 1: Planning")

            # Create story 
            draft_prompt = f"""
            [PERSONA]
            You are a Children's Book Author. Tone: Whimsical, Simple, Warm.
            
            [INPUT DATA]
            Plan: {json.dumps(plan_data['plan'])}
            
            [TASK]
            Write the story text for this part.
            
            [CONSTRAINTS]
            - Split into EXACTLY 3 distinct pages.
            - Max 3 sentences per page.
            - Vocabulary suitable for 5-year-olds.
            
            [FEW-SHOT EXAMPLES]
            Example Output Format:
            {{
                "pages": [
                    "Page 1 text goes here...",
                    "Page 2 text goes here...",
                    "Page 3 text goes here..."
                ]
            }}
            
            [GENERATE]
            Write the JSON for the current story part now.
            """
            draft_data = setup.generate_json(draft_prompt, "Step 2: Drafting")

            # Refine story 
            for page_idx, raw_text in enumerate(draft_data['pages']):
                refine_prompt = f"""
                [ROLE]
                You are a Strict Editor for children's content.
                
                [INPUT TEXT]
                "{raw_text}"
                
                [CRITERIA]
                1. Age Appropriateness: Is it simple enough for a 5-year-old?
                2. Consistency: Does it match {main_char['name']}'s traits?
                3. Safety: Are there any negative words?
                
                [TASK]
                Rewrite the text to be perfect.
                
                [OUTPUT]
                JSON: {{ "critique": "What you changed", "final_text": "The polished text" }}
                """
                refined_data = setup.generate_json(refine_prompt, f"Step 3: Refine Page {page_idx+1}")
                
               # Image prompt 
                img_prompt_req = f"""
                [TASK]
                Create an AI Image Generation Prompt for this text:
                "{refined_data['final_text']}"
                
                [REQUIREMENTS]
                - Describe the Background ({loc}).
                - Context: {config.background}
                - Describe Characters: {main_char['name']} and {sub_char['name']}.
                - Define Poses and Facial Expressions matching the text.
                - Visual Traits: {main_char.get('visuals', '')}
                
                [OUTPUT]
                JSON: {{ "image_prompt": "Visual description..." }}
                """
                img_data = setup.generate_json(img_prompt_req, f"Step 4: Image Prompt")
                
                #Asset generation
                img_filename = f"img_{page_global_counter}.png"
                audio_filename = f"audio_{page_global_counter}.mp3"
                img_path = os.path.join(story_folder, img_filename)
                audio_path = os.path.join(story_folder, audio_filename)
                
                print(f"Generating Image: {img_filename}")
                setup.generate_image(img_data['image_prompt'], img_path)
                print(f"Generating Audio: {audio_filename}")
                await setup.generate_audio(refined_data['final_text'], audio_path)

                # Store data
                full_story['pages'].append({
                    "pageNumber": page_global_counter,
                    "storyText": refined_data['final_text'],
                    "imageFileName": img_filename,
                    "audioFileName": audio_filename,
                    "planReasoning": plan_data['reasoning'],
                    "imagePrompt": img_data['image_prompt']
                })
                page_global_counter += 1

        # Save data
        json_path = os.path.join(story_folder, "story_data.json")
        with open(json_path, "w") as f:
            json.dump(full_story, f, indent=4)
        print(f"{story_id} Complete. Saved to {json_path}")

if __name__ == "__main__":
    asyncio.run(run_pipeline())