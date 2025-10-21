from click import prompt
import requests
from pathlib import Path
import os
import environ
from chatbot.models import Chat, Message
from core.models import Paciente
from openai import OpenAI
import json
from core.models import Paciente
env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = os.path.join(BASE_DIR, '.env')

client = OpenAI(
    api_key=env('deepseek_key'),
    base_url=env('deepseek_url')
)


if os.path.exists(env_file):
    environ.Env.read_env(env_file)
DEEPSEEK_API_URL= env('deepseek_url')
DEEPSEEK_API_KEY = env('deepseek_key')

def lookup_appointment(messages, chat: Chat):
    return f"Tu siguiente atencion sera en 1 dia"


def register_appointment(messages, chat: Chat):
    return 'Cita registrada'

def lookup_patient(messages, chat: Chat):
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
        chat.current_state = 'patient_registration'
        chat.current_sub_state = 'awaiting_data'
        chat.save()
        return f'''
        Veo que este numero no esta registrado en nuestro sistema,
        por favor envienos los siguientes datos para poder registrarlo:
        Nombre:
        Apellido:
        DNI:
        Fecha de Nacimiento:
    '''
    else:
        chat.current_state = 'data_confirmation'
        chat.current_sub_state = 'awaiting_confirmation'
        chat.save()
        return f'''
        Por favor confirme que estos sean sus datos antes de continuar:
        Nombre: {patient.nomb_pac} {patient.apel_pac}
        DNI: {patient.dni_pac}    
        Fecha de Nacimiento: {patient.fena_pac}
        Numero de Telefono: {patient.telf_pac}
        Direccion: {patient.dire_pac}
        '''
    
def data_confirmation(messages, chat: Chat):
    transcription, history = transcript_history(messages)

    if chat.current_sub_state == 'awaiting_confirmation':
        prompt = f"""
        You are an assistant that will determine if the users response confirms their personal data.
        Your response will be a json and have this format:
        {{
            "confirmation": boolean
        }}

        here is the user chat history, just check the last user message for confirmation:
        {transcription}
"""
        response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7,
                response_format={"type": "json_object"},
            )

        reply = response.choices[0].message.content.strip()
        data = json.loads(reply)     
        confirmation = data.get('confirmation', False)

        if confirmation:
            chat.data_confirmed = True
            chat.current_state = 'default' 
            chat.current_sub_state = 'default'
            chat.save()
            return "Gracias por confirmar sus datos. ¿Desea continuar con el registro de su Cita?"
        else:
            chat.current_state = 'patient_registration'
            chat.current_sub_state = 'awaiting_data'
            chat.save()
            return """Lamento el error. Por favor envíenos nuevamente sus datos para actualizar su información:
                Nombre:
                Apellido:
                DNI:
                Fecha de Nacimiento:"""

def register_patient(messages, chat: Chat):
    # extract patient data with LLM
    #data = extract_patient_info(messages)
    #patients.create_patient(data)

    transcription, history = transcript_history(messages)

    try:

        if chat.current_sub_state == 'awaiting_data':
            prompt = f"""
            You are an assistant that extracts personal information from patients in order to register them in a dental clinic.

            The patient must provide the following data:
            - DNI
            - Nombre
            - Apellido
            - Fecha de Nacimiento
            - Numero de Telefono

            Your task is to extract that information from the user's message and return it **only** as a valid JSON object in the following format:
            {{
                'dni': string,
                'nombre': string,
                'apellido': string,
                'fecha_nacimiento': string, # formato YYYY-MM-DD
                'telefono': string,
            }}

            Analyze the conversation below, but extract the information **only from the last patient message**:
            {transcription}
            """


            response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

            reply = response.choices[0].message.content.strip()

            reply = response.choices[0].message.content.strip()
            data = json.loads(reply)

            paciente = Paciente.objects.create(
                dni_pac=data.get('dni', ''),
                nomb_pac=data.get('nombre', ''),
                apel_pac=data.get('apellido', ''),
                fena_pac=data.get('fecha_nacimiento', ''),
                telf_pac=data.get('telefono', ''),
            )

            chat.current_state = 'default'
            chat.current_sub_state = 'default'
            chat.patient = paciente
            chat.save()

            return f"""Gracias {paciente.nomb_pac}, ya lo he registrado.
            Desea continuar con la programacion de una cita?"""
    except Exception as e:
        return f"Hubo un error al registrar sus datos, por favor intente de nuevo. Error: {str(e)}"

def default_chat(messages, chat: Chat):
    """
    Default fallback flow: continue a natural conversation with the patient.
    Uses the last N messages from the chat history.
    """

    transcript, history = transcript_history(messages)

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

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )

    reply = response.choices[0].message.content.strip()
    return reply, 'default'


def transcript_history(messages: list[Message]):
    # Convert chat history to plain text transcript
    history = []
    for msg in messages:
        speaker = "paciente" if msg.from_user else "tu"
        history.append(f"-{speaker}: {msg.text}")

    history = history[::-1]

    transcript = "\n".join(history)

    return transcript, history