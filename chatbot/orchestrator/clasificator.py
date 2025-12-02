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

# Define possible intents with description + example
INTENTS_AND_DESCRIPTIONS = {
    "lookup_apointmnet": {
        "description": "Cuando el paciente escoge una fecha para la cita, se asegura de que haya un horario disponible ese dia",
        "example": [
            {"user": "¿Hay alguna cita disponible este viernes?"},
            {"assistant": "Sí, tenemos espacio libre de las 2 PM a las 5 PM."},
        ]
    },
    "patient_registration": {
        "description": "Registrar informacion del paciente, en la practica esto nunca se dispara directamente aqui",
        "example": [
            'no applicable'
        ]
    },
    "default": {
        "description": "Charla general o preguntas no relacionadas con citas o registro de pacientes",
        "example": [
            {"user": "¿Qué servicios ofrecen?"},
            {"assistant": "Ofrecemos limpiezas, tratamientos dentales, ortodoncia y más."}
        ]
    },
    "data_confirmation": {
        "description": "Cuando el sistema quiera confirmar o actualizar los datos del paciente ya registrado, en la practica esto nunca se dispara directamente aqui",
        "example": [
            'no applicable'
        ]
    },
    "lookup_patient": {
        "description": "Asegurarse de que este chat tenga un paciente registrado, en la práctica esto nunca se dispara directamente aquí",
        "example": [
            'no applicable'
        ]
    },
    "appointment_registration": {
        "description": "Registrar una nueva cita, se suele activar luego de lookup_appointment, el paciente no tiene que decir directamente que quiere registrar una cita, es suficiente que el contexto lo sugiera",
        "example": [
            {"user": "Quiero sacar una cita para el martes."},
            {"assistant": "Tenemos disponibilidad el martes. ¿A qué hora le gustaría?"},
            {"user": "En la tarde, por favor."},
            {"assistant": "Perfecto, te registro el martes a las 4 PM."}
        ]
    }
}


def classify_intent(chat: Chat) -> str:
    messages = chat.last_messages()
    transcription, history = transcript_history(messages)

    # Build intent list as a simple string and full JSON for the LLM
    intents_list = ", ".join(INTENTS_AND_DESCRIPTIONS.keys())
    intents_json = json.dumps(INTENTS_AND_DESCRIPTIONS, ensure_ascii=False)

    # Build a prompt with the full intents dictionary and request JSON output
    prompt = f"""
Eres un clasificador de intenciones en español.

Debes devolver SOLO un JSON con la siguiente estructura:
{{
  "intent": "<una de: {intents_list}>",
  "confidence": 0.0
}}

Aquí tienes todas las intenciones posibles, cada una con su descripción y ejemplos de conversación:
{intents_json}

Toma en cuenta el mensaje del usuario (puede venir de una transcripción de audio):

Historial de mensajes del usuario:
\"\"\"{transcription}\"\"\"
"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60,
        temperature=0.0,
        response_format={"type": "json_object"},
    )

    # Parse JSON safely
    try:
        parsed = json.loads(resp.choices[0].message.content)
        intent = parsed.get("intent")
        confidence = float(parsed.get("confidence", 0.0))
    except Exception:
        intent, confidence = None, 0.0

    return intent if intent in INTENTS_AND_DESCRIPTIONS else "default"
