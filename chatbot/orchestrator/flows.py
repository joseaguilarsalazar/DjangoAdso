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

def lookup_appointment(text, chat):
   # next_slot = appointments.get_next_available(user)
    return f"Tu siguiente atencion sera en 1 dia"


def register_appointment(text, chat):
    return 'Cita registrada'

def lookup_patient(text, chat):
    return 'Has sido registrado'

def register_patient(text, chat):
    # extract patient data with LLM
    #data = extract_patient_info(text)
    #patients.create_patient(data)
    return "Tu informacion se registro con exito."

def default_chat(messages, chat):
    """
    Default fallback flow: continue a natural conversation with the patient.
    Uses the last N messages from the chat history.
    """

    # Convert chat history to plain text transcript
    history = []
    for msg in messages:
        speaker = "paciente" if msg.from_user else "tu"
        history.append(f"-{speaker}: {msg.text}")

    history = history.reverse()

    transcript = "\n".join(history)

    print(history[0])
    print(history[-1])

    # Insert your original prompt unchanged
    prompt = f"""
    Eres una chatbot, que trabaja para una clinica dental, tu rol es de atencion al cliente via whatsapp.
    Tienes que responder al cliente de la forma mas humana posible, haciendo las respuestas lo mas cortas posibles, mientras
    aun respondes las necesidades del cliente.

    ejemplo 1:
    -paciente: me duele una muela
    -tu: Ya veo, aqui en ADSO te podemos ayudar con nuestros servicios, te gustaria que se agendara una cita?

    ejemplo 2:
    -paciente: tengo problemas con mis curaciones
    -tu: Lamento escuchar eso, aqui en Adso podemos ayudarle, desea agendar una cita?

    ejemplo 3:
    -paciente: Buenas tardes, me dijeron que este es el numero del dentista
    -tu: Asi es, esta hablando con la clinica ADSO, en que podemos ayudarle?
    -paciente: Eh tenido problemas con mis braquets
    -tu: Entiendo, desearia que le agende una cita para revisarlo?

    tu objetivo es hacer que el paciente agende una cita con nosotros, si el paciente empieza a a hablar de temas
    no relacionados a la clinica dental le responderas asi:

    ejemplo 4:
    -paciente: A cuanto estan la computadoras?
    -tu: hola, te estas comunicando con ADSO, no podemos ayudarte con eso, somos una clinica dental, si necesesitas ayuda con algun tema de salud bucal estamos felizes de ayudarte
    
    Esta es la conversación reciente con el paciente, las ultimas interacciones, tu solo debes
    responder de forma coherente al ultimo mensaje, siguiendo el hilo de la conversacion:
    {transcript}

    Responde al último mensaje del paciente.
    """

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    reply = data["choices"][0]["message"]["content"].strip()
    return reply