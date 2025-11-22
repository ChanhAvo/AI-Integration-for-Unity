import time
import json
import edge_tts
from google import genai
from huggingface_hub import InferenceClient
from PIL import Image
import config  

# Setup APIs
google_client = genai.Client(api_key=config.GEMINI_API_KEY)
hf_client = InferenceClient(token=config.HF_TOKEN)

def clean_json(text):
    return text.replace("```json", "").replace("```", "").strip()

def generate_json(prompt, step_name):
    print(f"> AI Step: {step_name}...")
    try:
        response = google_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json', 
                'temperature': 0.7
            }
        )
        return json.loads(clean_json(response.text))

    except Exception as e:
        print(f"! Error in {step_name}: {e}. Retrying...")
        time.sleep(2)
        return generate_json(prompt, step_name)

def generate_image(prompt, filepath):
    try:
        final_prompt = f"A whimsical children's book illustration of {prompt}. Vibrant colors, soft lighting, high resolution, masterpiece."
        image = hf_client.text_to_image(
            final_prompt, 
            model=config.image_model
        )
        image.save(filepath)
    except Exception as e:
        print(f"    ! Image Gen Failed: {e}")
        img = Image.new('RGB', (512, 512), color='white')
        img.save(filepath) 

async def generate_audio(text, filepath):
    try:
        communicate = edge_tts.Communicate(text, "en-US-AnaNeural")
        await communicate.save(filepath)
    except Exception as e:
        print(f"! Audio Gen Failed: {e}")