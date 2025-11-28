# AI-Integration-for-Unity
📚 AI-Driven Storybook Generator & Interactive Reader

An automated pipeline that generates consistent multimedia children's stories using Generative AI and deploys them to an interactive Unity application.



📖 Overview

This project bridges the gap between Generative AI and Interactive Game Development. It addresses common challenges in AI storytelling—such as character inconsistency and hallucination—by implementing a structured "Blueprint & Seed" pipeline.

The system is composed of two distinct modules:

The AI Pipeline (Python): A batch-processing engine that orchestrates LLMs, Image Generators, and TTS to create cohesive story assets (JSON, PNG, MP3).

The Interactive Reader (Unity): A dynamic Unity application that loads these generated stories, allowing users to read, listen, and verify comprehension via an interactive Q&A module.


🛠️ Tech Stack

AI Backend (Python)

LLM: Google Gemini API

Image Gen: Hugging Face Inference API (Stable Diffusion XL)

TTS: edge-tts (Microsoft Edge Text-to-Speech)

Application Frontend (Unity)

Engine: Unity 

Language: C#

UI: TextMeshPro (TMP)

🚀 Installation & Usage

1. Generate Stories (Python)

Navigate to the AI_Pipeline folder and install dependencies:

```cd AI_Pipeline```

(Dependencies: google-genai, huggingface_hub, python-dotenv, edge-tts)

Create a .env file with your keys:

```GEMINI_API_KEY=your_google_key```

```HF_TOKEN=your_hugging_face_key```


Run the generator:

```python main.py```


The system will generate stories and automatically save them into ../Unity_Project/Assets/StreamingAssets/StoryData.

2. Play the App (Unity)

Open Unity Hub.

Add the Unity_Project folder.

Open MainScene.

Press Play. The menu will automatically detect and list the stories generated in Step 1.

📂 Project Structure
```
Repo_Root/
├── .gitignore              # Configured for Unity & Python
├── AI_Pipeline/            # Python Source Code
│   ├── config.py           # Character blueprints & World definitions
│   ├── main.py             # Entry point for batch generation
│   ├── story_generator.py  # Core logic (Plan -> Draft -> Refine)
|   ├── media_generator.py  # Generate image and voice audio
│   ├── prompts.py          # AI Persona definitions
│   └── setup.py            # API connectors
│
└── Unity_Project/          # Unity Source Project
    ├── Assets/
    │   ├── Scripts/        # C# Logic (StoryManager.cs)
    │   └── StreamingAssets/# GENERATED CONTENT REPOSITORY
    │       └── StoryData/  # Folders containing JSON, PNG, MP3s
    └── ProjectSettings/
```

🎥 Demo Preview


https://github.com/user-attachments/assets/c64157a6-8253-472f-acc4-5741d2877f4e



📄 License

This project is open-source and available for educational purposes.
