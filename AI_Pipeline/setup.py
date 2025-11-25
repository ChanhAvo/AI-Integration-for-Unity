import os
import time
import json
from pathlib import Path
import config
import prompts
from google import genai
from huggingface_hub import InferenceClient
import edge_tts
from PIL import Image


def _safe_write(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def log_prompt(name, prompt_text):
    safe_name = name.replace(" ", "_").replace("/", "_")
    path = os.path.join(config.PROMPT_LOG_DIR, f"{safe_name}.txt")
    _safe_write(path, prompt_text)
    return path

def log_response(name, obj):
    safe_name = name.replace(" ", "_").replace("/", "_")
    path = os.path.join(config.RESPONSE_LOG_DIR, f"{safe_name}.json")
    _safe_write(path, json.dumps(obj, ensure_ascii=False, indent=2))
    return path


def _extract_json_text(text):
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first:last+1]
    return None


def call_llm(prompt_text, step_name):
    log_prompt(step_name, prompt_text)
    if genai is None or config.GEMINI_API_KEY is None:
        fallback = {"fallback": True, "note": "genai missing or no API key"}
        log_response(step_name, fallback)
        return fallback

    client = genai.Client(api_key=config.GEMINI_API_KEY)
    attempts = 0
    while attempts < config.MAX_LLM_RETRIES:
        attempts += 1
        try:
            resp = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt_text,
                config={'response_mime_type': 'application/json', 'temperature': 0.7}
            )
            text = resp.text
            extracted = _extract_json_text(text)
            if extracted:
                parsed = json.loads(extracted)
                log_response(step_name, parsed)
                return parsed
            else:
                log_response(step_name + "_raw", {"raw": text})
                raise ValueError("LLM returned non-JSON / unparsable content")
        except Exception as e:
            err = str(e)
            print(f"[LLM] attempt {attempts}/{config.MAX_LLM_RETRIES} failed: {err}")
            if "429" in err or "rate" in err.lower():
                backoff = config.BASE_BACKOFF * (2 ** (attempts - 1))
                print(f"[LLM] rate-limited; backing off {backoff}s")
                time.sleep(backoff)
                continue
            if attempts >= config.MAX_LLM_RETRIES:
                print("[LLM] all attempts failed; returning fallback")
                fallback = {"fallback": True}
                log_response(step_name + "_fallback", fallback)
                return fallback
            time.sleep(1)

# Image generation
def generate_image(prompt_str, negative_prompt, seed, filepath, model_name=None):
    model_name = model_name or config.image_model
    _safe_write(filepath + ".prompt.txt", prompt_str)
    if InferenceClient is None or config.HF_TOKEN is None:
        Image.new("RGB", (512, 512), color="gray").save(filepath)
        return {"status": "placeholder", "note": "HF client missing or token missing"}
    client = InferenceClient(token=config.HF_TOKEN)
    try:
        image = client.text_to_image(
            prompt_str,
            negative_prompt=negative_prompt,
            model=model_name,
            seed=seed,
            width=1024,
            height=1024
        )
        if image.size != (512, 512):
            image = image.resize((512, 512), Image.Resampling.LANCZOS)
        image.save(filepath)
        return {"status": "ok"}
    except Exception as e:
        print(f"[SD] generation failed: {e}")
        Image.new("RGB", (512, 512), color="gray").save(filepath)
        return {"status": "failed", "error": str(e)}

# Audio generation
async def generate_audio(text, filepath):
    _safe_write(filepath + ".txt", text)
    if edge_tts is None:
        open(filepath, "wb").close()
        return {"status": "placeholder"}
    try:
        communicate = edge_tts.Communicate(text, "en-US-AnaNeural", rate="-10%", pitch="+1Hz")
        await communicate.save(filepath)
        return {"status": "ok"}
    except Exception as e:
        print(f"[TTS] failed: {e}")
        open(filepath, "wb").close()
        return {"status": "failed", "error": str(e)}

