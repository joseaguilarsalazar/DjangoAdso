import requests
from django.conf import settings
from pathlib import Path
import os
import environ

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = os.path.join(BASE_DIR, '.env')


if os.path.exists(env_file):
    environ.Env.read_env(env_file)

DEEPSEEK_API_URL = env('deepseek_url')
DEEPSEEK_API_KEY = env('deepseek_key')
# Define possible intents
INTENTS = ["appointment_lookup", "patient_registration", "default", 'data_confirmation']

def classify_intent(user_message: str) -> str:
    """
    Use DeepSeek API to classify a user message into a predefined intent.
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

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

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 10,
        "temperature": 0,
    }

    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    raw_output = data["choices"][0]["message"]["content"].strip().lower()

    # Validate result
    if raw_output in INTENTS:
        return raw_output
    else:
        return "default"
