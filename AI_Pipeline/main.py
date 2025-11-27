import os
import config
import time
import asyncio
from story_generator import generate_story

def choose_combinations(n=16):
    combos = []
    chars = config.characters
    locs = config.locations
    i = 0
    while len(combos) < n:
        main = chars[i % len(chars)]
        sub_index = (i + 1 + (i // len(chars))) % len(chars) 
        sub = chars[sub_index]
        
        if main["short_name"] == sub["short_name"]:
             sub = chars[(sub_index + 1) % len(chars)]

        loc = locs[i % len(locs)]
        combos.append((main, sub, loc))
        i += 1
    return combos

async def main_async(n=16):
    combos = choose_combinations(n)
    
    os.makedirs(config.output_dir, exist_ok=True)

    print(f"--- Starting Batch Generation for {n} Stories ---")
    print(f"Output Directory: {config.output_dir}")

    for idx, (main, sub, loc) in enumerate(combos):
        story_id = f"story_{idx+1:02d}"
        story_folder = os.path.join(config.output_dir, story_id)
        final_json_path = os.path.join(story_folder, "story_data.json")

        if os.path.exists(final_json_path):
            print(f"[SKIP] {story_id} already exists. Moving to next...")
            continue
        # --------------------

        print(f"\nGenerating {story_id}: {main['short_name']} + {sub['short_name']} @ {loc['name']}")
        try:
            await generate_story(story_id, main, sub, loc, config.output_dir)
        except Exception as e:
            print(f"Story {story_id} FAILED: {e}")
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(main_async(16))