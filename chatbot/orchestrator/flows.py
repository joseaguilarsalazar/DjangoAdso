import requests
from pathlib import Path
import os
import environ
from chatbot.models import Chat
from core.models import Paciente

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = os.path.join(BASE_DIR, '.env')


if os.path.exists(env_file):
    environ.Env.read_env(env_file)
DEEPSEEK_API_URL= env('deepseek_url')
DEEPSEEK_API_KEY = env('deepseek_key')

def lookup_appointment(text, chat: Chat):
    return f"Tu siguiente atencion sera en 1 dia"


def register_appointment(text, chat: Chat):
    return 'Cita registrada'

def lookup_patient(text, chat: Chat):
    patient = chat.patient if chat.patient else None
    there_patient = True if patient else False
    if not patient:
        number = chat.number.split('1')[1] if '1' in chat.number else chat.number
        if len(number) != 9:
             pass
        else:
            patient = Paciente.objects.filter(telf_pac=number).first()
        if not patient:
             pass
        else:
            chat.patient = patient
            chat.save()
            there_patient = True

    if not there_patient:
        return f'''
        Veo que este numero no esta registrado en nuestro sistema,
        por favor envienos los siguientes datos para poder registrarlo:
        Nombre:
        Apellido:
        DNI:
        Fecha de Nacimiento:
    ''', 'patient_registration'
    else:
        return f'''
        Por favor confirme que estos sean sus datos antes de continuar:
        Nombre: {patient.nomb_pac} {patient.apel_pac}
        DNI: {patient.dni_pac}    
        Fecha de Nacimiento: {patient.fena_pac}
        Numero de Telefono: {patient.telf_pac}
        Direccion: {patient.dire_pac}
        ''', 'data_confirmation'

def register_patient(text, chat: Chat):
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

    history = history[::-1]

    transcript = "\n".join(history)

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
    return reply, 'default'