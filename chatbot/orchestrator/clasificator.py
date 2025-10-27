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
INTENTS = ["appointment_lookup", "patient_registration", "default", "data_confirmation"]

def classify_intent(user_message: str) -> str:
    """
    Use DeepSeek (OpenAI-compatible API) to classify a user message into a predefined intent.
    """

    prompt = f"""
    You are an intent classifier for a dental clinic chatbot.
    Given the user message, classify it into one of the following intents:

    - appointment_lookup: when the user wants to check or book appointments
    - patient_registration: when the user wants to register/update personal data
    - data_confirmation: when the user is confirming their personal data
    - default: when it's just general talk, questions, or anything else

    Reply with only the intent keyword, nothing else.

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

        return raw_output if raw_output in INTENTS else "default"

    except Exception as e:
        # Optional: handle errors gracefully
        print(f"[DeepSeek Error] {e}")
        return "default"
