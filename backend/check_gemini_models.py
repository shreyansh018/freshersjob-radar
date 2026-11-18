import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)

print("\nFetching models available to your API key...\n")

try:
    models = client.models.list()

    count = 0

    for model in models:
        supported_actions = getattr(model, "supported_actions", []) or []

        if "generateContent" in supported_actions:
            model_name = model.name

            # Remove the "models/" prefix for convenient .env usage
            if model_name.startswith("models/"):
                model_name = model_name[len("models/"):]

            print(model_name)
            count += 1

    print(f"\nTotal models supporting generateContent: {count}")

except Exception as e:
    print(f"\nError fetching models: {e}")