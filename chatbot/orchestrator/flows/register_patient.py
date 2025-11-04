import json
from chatbot.models import Chat
from core.models import Paciente
from .trascript_history import transcript_history
from .AI_Client import client

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