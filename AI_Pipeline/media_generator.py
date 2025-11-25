import os
import config
import setup

def generate_image_for_prompt(sd_prompt: str, main_short: str, sub_short: str, location_name: str, page_index: int, out_dir: str):
    main = next((c for c in config.characters if c["short_name"] == main_short), None)
    sub = next((c for c in config.characters if c["short_name"] == sub_short), None)
    loc = next((l for l in config.locations if l["name"] == location_name), None)
    seed = ( (main or {}).get("seed",0) + (sub or {}).get("seed",0) + (loc or {}).get("seed",0) + page_index ) % 2147483647
    filename = f"page_{page_index:03d}.png"
    path = os.path.join(out_dir, filename)
    return setup.generate_image(sd_prompt, config.negative_prompt, seed, path, model_name=config.image_model)

async def generate_audio_for_text(text: str, page_index: int, out_dir: str):
    filename = f"page_{page_index:03d}.mp3"
    path = os.path.join(out_dir, filename)
    return await setup.generate_audio(text, path)
