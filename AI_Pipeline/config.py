import os 
from dotenv import load_dotenv

#Load keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

#Paths 
output_dir = "../Unity_Project/Assets/StreamingAssets/StoryData"
image_model = "black-forest-labs/FLUX.1-dev"

#Characters and locations 
characters = [
    {
        "name": "Little Red Riding Hood (Alice)",
        "role": "The Curious Explorer",
        "traits": "Innocent, inquisitive, brave yet easily bewildered. Chats with animals and questions the wolf. Carries a notebook to record oddities. Catchphrase: 'What a curious delight!'",
        "visuals": "Red hood, holding a pocket watch and dream-journal, dress trimmed with dream-like patterns."
    },
    {
        "name": "Aladdin (Jungle Boy)",
        "role": "The Wolf-Raised Survivor",
        "traits": "Clever and quick-thinking. Raised by wolves (Baloo & Bagheera). Climbs trees and uses wits to outsmart beasts. Longs to bridge the worlds of humans and animals.",
        "visuals": "Wild jungle boy appearance, wielding a torch of fire, agile pose, surrounded by jungle nature."
    },
    {
        "name": "Cinderella (Mechanic)", #Extra character
        "role": "The Tinkerer",
        "traits": "Builds gadgets from pumpkins, loves gears and oil. Practical and inventive.",
        "visuals": "Wearing grease-stained overalls, holding a wrench, steampunk aesthetic."
    },
    {
        "name": "Peter Pan (Pilot)", #Extra character
        "role": "The Flyer",
        "traits": "Flies a wooden plane, refuses to be serious. Adventurous and mischievous.",
        "visuals": "Aviator goggles, leather flight jacket, wooden propeller plane nearby."
    }
]
background = "Whistlewood Forest is a magical forest where trees hum gentle tunes and animals live in cozy treehouses."
locations = [
    "Melody Grove: A magical grove where trees sing when the wind blows.",
    "Berry Patch: A sweet-smelling field full of wild berries.",
    "Treehouse Village: Homes built high in the trees connected by rope bridges and lanterns.",
    "Echo Falls: A mystical waterfall that echoes back your laughter.",
    "Campfire Circle: A cozy gathering spot for telling stories and roasting marshmallows."]

story_structure = ["1. Setup", "2. Conflict", "3. Complication", "4. Climax", "5. Resolution", "6. Moral"]