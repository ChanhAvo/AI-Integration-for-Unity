import time
import json
import edge_tts
from huggingface_hub import InferenceClient
from google import genai
from PIL import Image
import config

# Setup APIs
google_client = genai.Client(api_key=config.GEMINI_API_KEY)
hf_client = InferenceClient(provider="nscale", token=config.HF_TOKEN)
def clean_json(text):
    return text.replace("```json", "").replace("```", "").strip()

def generate_json(prompt, step_name):
    print(f"AI Step: {step_name}...")
    
    while True:
        try:
            response = google_client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt,
                config={
                    'response_mime_type': 'application/json', 
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_output_tokens': 2048
                }
            )
            result = json.loads(clean_json(response.text))
            return result

        except json.JSONDecodeError:
            print(f"JSON Parse Error. Retrying...")
            time.sleep(2)
            continue
            
        except Exception as e:
            error_str = str(e)
            # Safe check for error codes in both string and object attributes
            is_rate_limit = "429" in error_str or getattr(e, 'code', 0) == 429
            is_server_error = "503" in error_str or "500" in error_str or getattr(e, 'code', 0) in [500, 503]

            if is_rate_limit:
                print(f"Rate Limit Hit (429). Sleeping 60 seconds to reset quota...")
                time.sleep(60) 
                continue
            
            elif is_server_error:
                print(f"Server Error. Sleeping 20 seconds...")
                time.sleep(20)
                continue
            
            else:
                print(f"Critical Error: {e}")
                return {"fallback": True, "error": str(e)}


def generate_image(scene_description, filepath, main_char_dict, sub_char_dict, location_dict, retry_count=0):
    try:
        main_bp = config.char_bp.get(main_char_dict['short_name'], {})
        sub_bp = config.char_bp.get(sub_char_dict['short_name'], {})
        loc_bp = config.loc_bp.get(location_dict['name'], {})
        
        style_tags = f"{config.global_style['art_style']}, {config.global_style['lighting']}, {config.global_style['technical']}"
        
        char1_desc = f"((({main_bp.get('core_identity', '')}))), ({main_bp.get('always_include', '')}:1.5)"
        char2_desc = f"((({sub_bp.get('core_identity', '')}))), ({sub_bp.get('always_include', '')}:1.5)"
        
        final_prompt = (
            f"{config.consistency_rules}. " 
            f"{style_tags}. "
            f"FOCUS CHARACTERS: {char1_desc}, {char2_desc}. "
            f"SCENE ACTION: {scene_description}. "
            f"ENVIRONMENT: {loc_bp.get('visual_identity', '')}. "
            f"Masterpiece, best quality, 8k, highly detailed, consistent character design."
        )

        # Negative Prompt 
        neg_prompt = (
            "ugly, deformed, noisy, blurry, low quality, text, watermark, "
            "bad anatomy, distortion, extra limbs, mutation, disconnected limbs, "
            "floating objects, objects passing through each other, bad hands, "
            "missing fingers, extra fingers, weird eyes, dull colors, "
            "changing clothes, different face, changing hair color, morphing"
        )
        
        # Calculate combined seed for consistency
        combined_seed = (
            main_char_dict.get('seed', 0) + 
            sub_char_dict.get('seed', 0) + 
            location_dict.get('seed', 0)
        ) % 2147483647
        
        
        if retry_count == 0:
            print(f"Using combined seed: {combined_seed}")
            print(f"Characters: {main_char_dict['short_name']} + {sub_char_dict['short_name']}")
        
        try:
            image = hf_client.text_to_image(
                final_prompt,
                negative_prompt=neg_prompt, 
                model=config.image_model,
                seed=combined_seed,
                width=1024, 
                height=1024
            )
            
            if image.size != (512, 512):
                image = image.resize((512, 512), Image.Resampling.LANCZOS)
            
            image.save(filepath)
            print(f"Image saved: {filepath}")
            return 

        except Exception as e:
            error_str = str(e)
            if "503" in error_str or "429" in error_str:
                if retry_count < 5:
                    wait_time = (2 ** retry_count) * 20
                    print(f"Provider Busy. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    return generate_image(scene_description, filepath, main_char_dict, sub_char_dict, location_dict, retry_count + 1)
            raise e 

    except Exception as e:
        print(f"Image Gen Failed: {e}")
        img = Image.new('RGB', (512, 512), color='gray')
        img.save(filepath)
        print(f"Placeholder (Gray) saved")
        


async def generate_audio(text, filepath):
    try:
        communicate = edge_tts.Communicate(
            text, 
            "en-US-AnaNeural",  
            rate="-10%",  
            pitch="+1Hz" 
        )
        await communicate.save(filepath)
        print(f"Audio saved: {filepath}")
        
    except Exception as e:
        print(f"Audio Gen Failed: {e}")
        print(f"Audio file not created")