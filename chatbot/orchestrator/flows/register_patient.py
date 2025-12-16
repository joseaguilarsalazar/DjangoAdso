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
            
            And this data you must get from conversation context:
            - We are registering phone owner data, or from someone else? (child, parent, relative, friend, etc)

            Your task is to extract that information from the user's message and return it **only** as a valid JSON object in the following format:
            {{
                'dni': string,
                'nombre': string,
                'apellido': string,
                'fecha_nacimiento': string, # formato YYYY-MM-DD
                'ciudad_de_residencia': string (optional) #opciones por ahora Iquitos, Yurimaguas
                'is_phone_owner': boolean
            }}

            ### Extraction Logic:
            1. **Dates:** Convert any relative dates (like "born in 1990") to YYYY-MM-DD.
            2. **Phone Owner:** - Set 'is_phone_owner': true if the user implies the appointment is for themselves (e.g., "I need an appointment").
            - Set 'is_phone_owner': false if they mention a third party (son, mother, friend).
            3. **Scope:** Analyze the input text strictly. Do not invent information.

            ### Input Text:
            {transcription}
            """


            response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

            data = json.loads(response.choices[0].message.content)
            clinica_id = None
            if data.get('ciudad_de_residencia', None):
                from core.models import Clinica
                clinica_id = 1 if data['ciudad_de_residencia'].lower() == 'iquitos' else 2
            paciente = Paciente.objects.create(
                dni_pac=data.get('dni', ''),
                nomb_pac=data.get('nombre', ''),
                apel_pac=data.get('apellido', ''),
                fena_pac=data.get('fecha_nacimiento', ''),
                clinica=Clinica.objects.get(id=clinica_id) if clinica_id else None
            )

            chat.current_state = 'default'
            chat.current_sub_state = 'default'

            if not chat.extra_data.get('patients', None):
                chat.extra_data['patients'] = []

            chat.extra_data['patients'].append({
                'nombre': paciente.nomb_pac,
                'apellido': paciente.apel_pac,
                'dni': paciente.dni_pac,
                'fecha_nacimiento': str(paciente.fena_pac),
                'clinica_id': clinica_id,
                'patient_id': paciente.id,
                'is_phone_owner': data.get('is_phone_owner', False)
            })
            chat.save()

            return f"""Gracias, ya estan registrados sus datos.
            Desea continuar con la programacion de la cita?"""
    except Exception as e:
        return f"Hubo un error al registrar sus datos, por favor intente de nuevo. Error: {str(e)}"