import os 
from dotenv import load_dotenv

# Load keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Paths 
output_dir = "../Unity_Project/Assets/StreamingAssets/StoryData"
image_model = "stabilityai/stable-diffusion-xl-base-1.0"

# Characters and locations 
characters = [
    {
        "name": "Little Red Riding Hood (Alice)",
        "short_name": "Alice",  # Added for easy lookup
        "role": "The Curious Explorer",
        "traits": "Innocent, inquisitive, brave yet easily bewildered. Chats with animals and questions the wolf. Carries a notebook to record oddities. Catchphrase: 'What a curious delight!'",
        "visuals": "Red hood, holding a pocket watch and dream-journal, dress trimmed with dream-like patterns.",
        "seed": 12345  # Unique seed per character
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

background = "Whistlewood Forest is a magical forest where trees hum gentle tunes and animals live in cozy treehouses."

locations = [
    {
        "name": "Melody Grove",
        "description": "A magical grove where trees sing when the wind blows.",
        "seed": 11111
    },
    {
        "name": "Berry Patch",
        "description": "A sweet-smelling field full of wild berries.",
        "seed": 22222
    },
    {
        "name": "Treehouse Village",
        "description": "Homes built high in the trees connected by rope bridges and lanterns.",
        "seed": 33333
    },
    {
        "name": "Echo Falls",
        "description": "A mystical waterfall that echoes back your laughter.",
        "seed": 44444
    },
    {
        "name": "Campfire Circle",
        "description": "A cozy gathering spot for telling stories and roasting marshmallows.",
        "seed": 55555
    }
]

story_structure = ["1. Setup", "2. Conflict", "3. Complication", "4. Climax", "5. Resolution", "6. Moral"]

#Consistency blueprints
char_bp = {
    "Alice": {
        "core_identity": "a young 7-year-old girl with shoulder-length wavy brown hair, bright curious blue eyes, round face with rosy cheeks, wearing a bright red hooded cape with white trim over a blue dress with white apron",
        "always_include": "red hood cape, blue dress, white apron, wavy brown hair, blue eyes, holding a small brown notebook and silver pocket watch on a chain",
        "style_tags": "consistent character design, same face every time, same outfit every time, children's book illustration style",
        "quality_notes": "child NOT adult, storybook art NOT realistic photo, clear NOT blurry, bright NOT dark or scary"
    },
    "Jungle Boy": {
        "core_identity": "a lean 8-year-old boy with messy black hair, tan skin, brown eyes, wearing tattered brown shorts and vine wrappings, bare chest with small tribal necklace",
        "always_include": "messy black spiky hair, tan skin, brown eyes, brown torn shorts, vine arm wrappings, holding a wooden torch with orange flame, bare feet",
        "style_tags": "consistent character design, same face every time, same wild boy appearance, children's book illustration style",
        "quality_notes": "child NOT adult, jungle clothing NOT modern clothes, barefoot NOT wearing shoes, storybook art NOT realistic photo"
    },
    "Cinderella": {
        "core_identity": "a 9-year-old girl with blonde hair in a high ponytail, blue eyes, fair skin, wearing blue grease-stained overalls over a white shirt, round brass goggles pushed up on forehead",
        "always_include": "blonde ponytail, blue eyes, blue overalls with grease stains, white shirt underneath, brass steampunk goggles on head, holding a silver wrench",
        "style_tags": "consistent character design, same face every time, same mechanic outfit, children's book illustration style",
        "quality_notes": "mechanic overalls NOT ballgown or princess dress, working clothes NOT clean formal attire, child NOT adult"
    },
    "Peter Pan": {
        "core_identity": "a 10-year-old boy with messy red hair, green eyes, mischievous smile, wearing a brown leather aviator jacket over green shirt, tan pants, aviator goggles hanging around neck",
        "always_include": "messy red hair, green eyes, mischievous grin, brown leather jacket, green shirt, tan pants, aviator goggles around neck, small wooden toy airplane in hand or nearby",
        "style_tags": "consistent character design, same face every time, same pilot outfit, children's book illustration style",
        "quality_notes": "toy wooden plane NOT modern jet, child NOT adult, playful expression NOT serious, storybook art NOT realistic photo"
    }
}

loc_bp = {
    "Melody Grove": {
        "visual_identity": "a magical forest grove with tall ancient trees that have glowing musical note symbols floating around their branches, soft green grass floor, dappled golden sunlight filtering through leaves",
        "atmosphere": "warm, peaceful, musical, enchanted forest feeling",
        "colors": "green foliage, golden sunlight, soft glowing blue-white musical notes",
        "always_include": "singing trees with musical notes, forest setting, warm lighting"
    },
    "Berry Patch": {
        "visual_identity": "an open sunny meadow filled with colorful berry bushes heavy with bright red, blue, and purple berries, butterflies flying around, clear blue sky above",
        "atmosphere": "bright, cheerful, sweet-smelling, sunny day",
        "colors": "vibrant reds, blues, purples from berries, green bushes, bright yellow sunlight",
        "always_include": "berry bushes, colorful berries, sunny meadow, butterflies"
    },
    "Treehouse Village": {
        "visual_identity": "multiple wooden treehouses built into large tree trunks, connected by rope bridges, warm glowing lanterns hanging from branches, cozy windows with curtains",
        "atmosphere": "cozy, communal, elevated, safe and welcoming",
        "colors": "warm brown wood, golden lantern light, green tree leaves, rope bridges",
        "always_include": "wooden treehouses, rope bridges, hanging lanterns, tree branches"
    },
    "Echo Falls": {
        "visual_identity": "a tall sparkling waterfall cascading down moss-covered rocks, rainbow mist in the air, visible sound wave ripples in the pool below, glowing crystal formations",
        "atmosphere": "mystical, echoing, magical, water sounds",
        "colors": "blue-white water, rainbow mist, green moss, sparkling crystals",
        "always_include": "waterfall, rainbow mist, magical atmosphere, water pool"
    },
    "Campfire Circle": {
        "visual_identity": "a cozy clearing with a warm crackling campfire in the center, logs arranged in a circle for seating, marshmallows on sticks, starry night sky above with glowing fireflies",
        "atmosphere": "warm, cozy, nighttime, storytelling mood",
        "colors": "orange-red fire glow, dark blue night sky, twinkling stars, golden fireflies",
        "always_include": "campfire, log seating, night sky, warm glow"
    }
}

global_style = {
    "art_style": "whimsical children's book illustration, soft painterly style, warm and inviting, storybook quality, gentle rounded shapes, NO realistic photography",
    "color_palette": "warm and vibrant colors, soft pastel tones with pops of bright primary colors, consistent saturation across all images",
    "lighting": "soft natural lighting, warm gentle shadows, magical glow effects where appropriate",
    "composition": "medium shot showing full characters and environment, child eye-level perspective, clear focal point",
    "technical": "high quality, detailed, 4K resolution, professional children's book illustration standard"
}


consistency_rules = """
CRITICAL CONSISTENCY RULES - MUST FOLLOW:
1. Characters MUST look IDENTICAL in every single image - same face, same hair, same outfit, same proportions
2. Use the EXACT character descriptions provided - do not improvise or change ANY details
3. Locations MUST maintain the same visual identity and color scheme throughout
4. Art style MUST remain consistent - same painting technique, same level of detail
5. If a character appears in multiple pages, they must be THE SAME CHARACTER with THE SAME APPEARANCE
6. Color palette should be harmonious and consistent across all images
7. Do NOT add random elements not specified in the description
8. Keep the same "camera angle" and framing style throughout the story
"""