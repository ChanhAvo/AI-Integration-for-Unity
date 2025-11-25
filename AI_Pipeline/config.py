import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")


output_dir =  "../Unity_Project/Assets/StreamingAssets/StoryData"
Path(output_dir).mkdir(parents=True, exist_ok=True)
image_model =  "stabilityai/stable-diffusion-xl-base-1.0"


background = "Whistlewood Forest is a magical forest where trees hum gentle tunes and animals live in cozy treehouses."


characters = [
    {
        "name": "Little Red Riding Hood (Alice)",
        "short_name": "Alice",
        "role": "The Curious Explorer",
        "traits": "Innocent, inquisitive, brave yet easily bewildered. Chats with animals and questions the wolf. Carries a notebook to record oddities. Catchphrase: 'What a curious delight!'",
        "visuals": "Red hood, holding a pocket watch and dream-journal, dress trimmed with dream-like patterns.",
        "seed": 12345
    },
    {
        "name": "Aladdin (Jungle Boy)",
        "short_name": "Jungle Boy",
        "role": "The Wolf-Raised Survivor",
        "traits": "Clever and quick-thinking. Raised by wolves (Baloo & Bagheera). Climbs trees and uses wits to outsmart beasts. Longs to bridge the worlds of humans and animals.",
        "visuals": "Wild jungle boy appearance, wielding a torch of fire, agile pose, surrounded by jungle nature.",
        "seed": 23456
    },
    {
        "name": "Cinderella (Mechanic)",
        "short_name": "Cinderella",
        "role": "The Tinkerer",
        "traits": "Builds gadgets from pumpkins, loves gears and oil. Practical and inventive.",
        "visuals": "Wearing grease-stained overalls, holding a wrench, steampunk aesthetic.",
        "seed": 34567
    },
    {
        "name": "Peter Pan (Pilot)",
        "short_name": "Peter Pan",
        "role": "The Flyer",
        "traits": "Flies a wooden plane, refuses to be serious. Adventurous and mischievous.",
        "visuals": "Aviator goggles, leather flight jacket, wooden propeller plane nearby.",
        "seed": 45678
    }
]

locations = [
    {"name": "Melody Grove", "description": "A magical grove where trees sing when the wind blows.", "seed": 11111},
    {"name": "Berry Patch", "description": "A sweet-smelling field full of wild berries.", "seed": 22222},
    {"name": "Treehouse Village", "description": "Homes built high in the trees connected by rope bridges and lanterns.", "seed": 33333},
    {"name": "Echo Falls", "description": "A mystical waterfall that echoes back your laughter.", "seed": 44444},
    {"name": "Campfire Circle", "description": "A cozy gathering spot for telling stories and roasting marshmallows.", "seed": 55555}
]

#story structure 
story_structure = ["1. Setup", "2. Conflict", "3. Complication", "4. Climax", "5. Resolution", "6. Moral"]

#Character & location blueprints 
char_bp = {
    "Alice": {
        "core_identity": "a young 7-year-old girl with shoulder-length wavy brown hair, bright curious blue eyes, round face with rosy cheeks",
        "always_include": "red hood cape, blue dress, white apron, wavy brown hair, blue eyes, holding a small brown notebook and silver pocket watch on a chain",
        "style_tags": "consistent character design, same face every time, same outfit every time, children's book illustration style",
        "quality_notes": "child NOT adult, storybook art NOT realistic photo, clear NOT blurry, bright NOT dark or scary"
    },
    "Jungle Boy": {
        "core_identity": "a lean 8-year-old boy with messy black hair, tan skin, brown eyes",
        "always_include": "messy black spiky hair, tan skin, brown eyes, brown torn shorts, vine arm wrappings, holding a wooden torch with orange flame, bare feet",
        "style_tags": "consistent character design, same face every time, same wild boy appearance, children's book illustration style",
        "quality_notes": "child NOT adult, jungle clothing NOT modern clothes, barefoot NOT wearing shoes, storybook art NOT realistic photo"
    },
    "Cinderella": {
        "core_identity": "a 9-year-old girl with blonde hair in a high ponytail, blue eyes, fair skin",
        "always_include": "blonde ponytail, blue eyes, blue overalls with grease stains, white shirt underneath, brass steampunk goggles on head, holding a silver wrench",
        "style_tags": "consistent character design, same face every time, same mechanic outfit, children's book illustration style",
        "quality_notes": "mechanic overalls NOT ballgown or princess dress, working clothes NOT clean formal attire, child NOT adult"
    },
    "Peter Pan": {
        "core_identity": "a 10-year-old boy with messy red hair, green eyes, mischievous smile",
        "always_include": "messy red hair, green eyes, mischievous grin, brown leather jacket, green shirt, tan pants, aviator goggles around neck, small wooden toy airplane nearby",
        "style_tags": "consistent character design, same face every time, same pilot outfit, children's book illustration style",
        "quality_notes": "toy wooden plane NOT modern jet, child NOT adult, playful expression NOT serious, storybook art NOT realistic photo"
    }
}

loc_bp = {
    "Melody Grove": {
        "visual_identity": "tall ancient trees with glowing musical-note glyphs floating around branches, soft green grass, golden dappled sunlight",
        "atmosphere": "warm, peaceful, musical, enchanted",
        "always_include": "singing trees with floating musical notes, warm sunlight"
    },
    "Berry Patch": {
        "visual_identity": "open sunny meadow with dense berry bushes heavy with bright berries and fluttering butterflies",
        "atmosphere": "bright, cheerful, sweet-smelling",
        "always_include": "berry bushes, butterflies, sunny sky"
    },
    "Treehouse Village": {
        "visual_identity": "wooden treehouses, rope bridges, lanterns, cozy windows",
        "atmosphere": "cozy, communal, elevated",
        "always_include": "treehouses, rope bridges, lantern light"
    },
    "Echo Falls": {
        "visual_identity": "a sparkling waterfall cascading over mossy rocks, rainbow mist above the pool, subtle sound-wave ripples",
        "atmosphere": "mystical, echoing, playful",
        "always_include": "waterfall, rainbow mist, echoing sound visuals"
    },
    "Campfire Circle": {
        "visual_identity": "a clearing with a warm crackling campfire, logs in a circle, fireflies and starry night",
        "atmosphere": "warm, cozy, storytelling",
        "always_include": "campfire, logs, night sky, fireflies"
    }
}

# Global visual style
global_style = {
    "art_style": "whimsical children's book illustration, soft painterly style, warm and inviting",
    "color_palette": "warm pastels with pops of bright primary colors",
    "lighting": "soft natural lighting with gentle glows",
    "composition": "medium shot, child eye-level, clear focal point",
    "technical": "high-detail, illustration-quality (NOT photorealistic)"
}
# Negative prompt
negative_prompt = "ugly, deformed, noisy, blurry, text, watermark, bad anatomy, extra limbs, mutation, scary, gore, photorealistic, adult proportions"

# Word length range
word_min = 450
word_max = 850

# Reporting
REPORT_DIR = os.getenv("REPORT_DIR", "./reports")
PROMPT_LOG_DIR = os.path.join(REPORT_DIR, "prompts")
RESPONSE_LOG_DIR = os.path.join(REPORT_DIR, "responses")
Path(PROMPT_LOG_DIR).mkdir(parents=True, exist_ok=True)
Path(RESPONSE_LOG_DIR).mkdir(parents=True, exist_ok=True)

MAX_LLM_RETRIES = 6
BASE_BACKOFF = 2  
