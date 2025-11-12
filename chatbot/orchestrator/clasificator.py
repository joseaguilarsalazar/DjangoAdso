from openai import OpenAI
from django.conf import settings
from pathlib import Path
import os
import environ
from chatbot.models import Chat
from .flows.trascript_history import transcript_history
import json

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

def simple_rule_detector(transcription: str) -> str | None:
    txt = transcription.lower()
    # appointment keywords (spanish)
    if any(kw in txt for kw in ("cita", "sacar cita", "agendar", "turno", "reservar")):
        return "appointment_lookup"
    if any(kw in txt for kw in ("registro", "registrar", "dni", "nombre", "apellido")):
        return "patient_registration"
    # detect explicit DNI patterns or date patterns (regex)
    # return the matching intent or None
    return None

def classify_intent(chat: Chat) -> str:
    messages = chat.last_messages()
    transcription, history = transcript_history(messages)

    # First, quick deterministic rule check
    rule = simple_rule_detector(transcription)
    # Build a prompt with few-shot examples and request JSON output
    prompt = f"""
    Eres un clasificador de intenciones (español). Devuelve SOLO un JSON con campos:
    {{ "intent": "...", "confidence": 0.0 }}
    Posibles intents: appointment_lookup, patient_registration, default, data_confirmation, lookup_patient, appointment_registration

    Ejemplos:
    Mensaje: "Quisiera sacar una cita para el martes"
    Intent: appointment_lookup

    Mensaje: "No recuerdo mis datos, me podrías registrar?"
    Intent: patient_registration

    Mensaje: "¿Cuáles son sus horarios?"
    Intent: default

    Mensaje: "{transcription}"
    """
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"user","content":prompt}],
        max_tokens=60,
        temperature=0.0,
        response_format={"type":"json_object"},
    )
    # Parse JSON safely
    try:
        parsed = json.loads(resp.choices[0].message.content)
        intent = parsed.get("intent")
        confidence = float(parsed.get("confidence", 0.0))
    except Exception:
        intent, confidence = None, 0.0

    # Combine: if rule and model disagree with low confidence -> prefer rule
    if intent is None or confidence < 0.65:
        if rule:
            return rule
    return intent if intent in INTENTS_AND_DESCRIPTIONS else "default"
