import config
from story_generator import generate_story

def choose_combinations(n=16):
    combos = []
    chars = config.characters
    locs = config.locations
    i = 0
    while len(combos) < n:
        main = chars[i % len(chars)]
        sub = chars[(i + 1) % len(chars)]
        if main["short_name"] == sub["short_name"]:
            sub = chars[(i + 2) % len(chars)]
        loc = locs[i % len(locs)]
        combos.append((main, sub, loc))
        i += 1
    return combos

def run_all(n=16):
    combos = choose_combinations(n)
    for idx, (main, sub, loc) in enumerate(combos):
        story_id = f"story_{idx+1:02d}"
        print(f"Generating {story_id}: {main['short_name']} + {sub['short_name']} @ {loc['name']}")
        try:
            generate_story(story_id, main, sub, loc, config.output_dir)
        except Exception as e:
            print(f"Story {story_id} failed: {e}")

if __name__ == "__main__":
    run_all(16)
