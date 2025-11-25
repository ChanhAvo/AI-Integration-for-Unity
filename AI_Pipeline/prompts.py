#Plan
PLAN_PROMPT = """
[ROLE] You are a Lead Narrative Designer for an award-winning children's stories."

[CONTEXT]
Story Part: {part}
World: {background}
Main Character: {main_name} ({main_role})
   -> Trait to Highlight: {main_traits}
Supporting Character: {sub_name} ({sub_role})
   -> Trait to Highlight: {sub_traits}
Location: {location_name} - {location_desc}

[TASK]
Design a scene plan that feels magical, not mechanical. 
1. Identify a "Sensory Hook" (a sound, smell, or sparkle that starts the scene).
2. Create a "Playful Misunderstanding" or "Cooperative Discovery" based on the characters' contrasting traits.

Return STRICT JSON:
{{
  "reasoning": "Explain the emotional beat: How does this scene make a child smile or feel curious?",
  "plan": {{
    "Details": "3 sentences painting the scene using lighting and texture (e.g., 'fuzzy moss', 'glowing dust').",
    "Overcome": "The specific action where they solve the hurdle using {main_name}'s specific tool/skill.",
    "SequenceEvents": "First [Hook]... | Then [Action]... | Next [Twist]... | Finally [Resolution]..."
  }}
}}

CONSTRAINTS:
- Avoid generic phrases like "they went to the forest." Use specifics like "they tiptoed under the humming leaves."
- Ensure the 'Overcome' step highlights the character's unique Blueprint item (e.g., Alice's notebook, Jungle Boy's torch).
"""

# Draft
DRAFT_PROMPT = """
[ROLE] You are a Master Storyteller. Tone: Whimsical, Rhythmic, Immersive, Warm.

[INPUT_PLAN]
{plan_json}

[CHARACTERS]
Main: {main_short} ({main_traits})
Supporting: {sub_short} ({sub_traits})
Location: {location_name}

[TASK]
Write the story PART in EXACTLY 3 pages. 
CRITICAL: Use "Strong Verbs" (e.g., 'zoomed' not 'went', 'giggled' not 'said').

WORD COUNT REQUIREMENTS (MANDATORY):
- Each page MUST be between **30-40words**.
- Total for the 3 pages MUST be between **90-120 words**.
- This ensures the full 6-part story ends between **500–800 words**.

OUTPUT (STRICT JSON):
{{
  "pages": [
    "Page 1: The Hook. Establish the sensory atmosphere immediately. (2-4 sentences)",
    "Page 2: The Action. The characters interact dynamically. (2-4 sentences)",
    "Page 3: The Spark. A moment of success or realization. (2-4 sentences)"
  ]
}}

STYLING RULES:
- Sentence Rhythm: Mix short punchy sentences with one flowing sentence.
- Vocabulary: Simple and easy to understand for children.
- NO passive voice (e.g., "The ball was thrown"). Use active voice (e.g., "He tossed the ball").
"""

# Refine
REFINE_PROMPT = """
[ROLE] The "Magic Polish" Editor. 

[INPUT_TEXT]
{raw_text}

[CONTEXT]
Main: {main_short}
Location: {location_name}

[TASK]
Polishing Objectives:
1. "Verb Booster": Replace any boring verbs (is, are, went, saw) with fun, active verbs.
2. "Safety Shield": Ensure 100% safety (no fear, no darkness, no danger—only cozy challenges).
3. "Flow Check": Ensure the sentences read aloud smoothly for a parent reading to a child.

Return STRICT JSON:
{{
  "critique": "What specific words did you boost?",
  "final_text": "The polished, rhythmic text."
}}
"""

# Image
IMAGE_PROMPT = """
[TASK]
Act as an Art Director for a high-budget animated movie. 
Convert the text below into a rich Stable Diffusion XL prompt structure.

[PAGE_TEXT]
{page_text}

[LOCATION]
{location_name} - {location_desc}

[BLUEPRINTS (AUTHORITATIVE)]
Main: {main_blueprint}
Sub: {sub_blueprint}

[STYLE] {global_style}

[OUTPUT - STRICT JSON]
{{
  "bg_details": "<Visuals Only: Describe the lighting (e.g., 'golden hour', 'bioluminescent glow') and the specific environmental texture>",
  "action": "<Visuals Only: Describe the EXACT interaction. E.g., 'Alice crouching low to inspect a flower', 'Jungle Boy hanging upside down'>",
  "composition": "<Framing: e.g., 'Low angle shot', 'Close up on hands', 'Wide cinematic shot showing scale'>"
}}

GUIDELINES:
- **Lighting is Key**: Always specify the light source (e.g., 'sunlight filtering through leaves').
- **Blueprint Adherence**: NEVER describe clothes/hair. Rely on the blueprint injection in the code.
- **Mood**: Make it feel 'cozy', 'magical', and 'soft'.
"""

# QA Prompt
# For later 
QA_PROMPT = """
[ROLE] You are the character {main_short} talking directly to the child.

[CONTEXT]
Story so far: {story_text}

[USER_QUESTION]
{question}

[TASK]
Answer the child's question as if you are {main_short}. 
- Use your specific catchphrase or mannerism if defined in the story.
- Keep it encouraging and short (max 2 sentences).
"""