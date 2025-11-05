from openai import OpenAI
from django.conf import settings
from pathlib import Path
import os
import environ

env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_file):
    environ.Env.read_env(env_file)

DEEPSEEK_API_URL = env('deepseek_url')  # e.g. https://api.deepseek.com/v1
DEEPSEEK_API_KEY = env('deepseek_key')

# Initialize OpenAI client (compatible with DeepSeek)
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_URL
)

# Define possible intents
INTENTS_AND_DESCRIPTIONS = {
    "appointment_lookup": "Check or book appointments",
    "patient_registration": "Register or update personal data",
    "default": "General talk or questions",
    "data_confirmation": "Confirm personal data",
    "lookup_patient": "Look up patient information",
    "appointment_registration": "Register a new appointment"
}

def classify_intent(user_message: str) -> str:
    """
    Use DeepSeek (OpenAI-compatible API) to classify a user message into a predefined intent.
    """

    prompt = f"""
    You are an intent classifier for a dental clinic chatbot.
    Given the user message, classify it into one of the following intents:

    """
    for intent, description in INTENTS_AND_DESCRIPTIONS.items():
        prompt += f"- {intent}: {description}\n"
    
    prompt += f"""

    return only the keyword of the intent that best matches the, nothing else.
    User message: "{user_message}"
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0,
        )

        raw_output = response.choices[0].message.content.strip().lower()

        return raw_output if raw_output in INTENTS_AND_DESCRIPTIONS.keys() else "default"

    except Exception as e:
        # Optional: handle errors gracefully
        print(f"[DeepSeek Error] {e}")
        return "default"
