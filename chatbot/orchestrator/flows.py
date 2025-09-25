import requests
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
DEEPSEEK_API_URL= env('deepseek_url')
DEEPSEEK_API_KEY = env('deepseek_key')

def lookup_appointment(text, user):
   # next_slot = appointments.get_next_available(user)
    return f"Tu siguiente atencion sera en 1 dia"

def register_patient(text, user):
    # extract patient data with LLM
    #data = extract_patient_info(text)
    #patients.create_patient(data)
    return "Tu informacion se registro con exito."

def default_chat(text):
    """
    Use DeepSeek API to classify a user message into a predefined intent.
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = f"""
    Eres una chatbot, que trabaja para una clinica dental, tu rol es de atencion al cliente via whatsapp.
    Tienes que responder al cliente de la forma mas humana posible, haciendo las respuestas lo mas cortas posibles, mientras
    aun respondes las necesidades del cliente.

    ejemplo:
    -paciente: me duele una muela
    -tu: Ya veo, aqui en ADSO te podemos ayudar con nuestros servicios, te gustaria que se agendara una cita?


    Este es el mensaje del usuario al que debes responder: 
    
    "{text}"
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

    response = data["choices"][0]["message"]["content"].strip().lower()

    return response