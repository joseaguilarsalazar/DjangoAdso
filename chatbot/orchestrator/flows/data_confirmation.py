from chatbot.models import Chat
from .AI_Client import client
import json
from .trascript_history import transcript_history
from core.models import Paciente

def data_confirmation(messages, chat: Chat):
    transcription, history = transcript_history(messages)
    if chat.current_sub_state == 'default':
        #the user gives dni, name or lastname to confirm data use ai to retrieve patient data
        #and then confirm it in the database in the Paciente model
        #if user exists send to user and pass to awaiting_confirmation
        #else ask for registration
        prompt = f"""
        The user will provide you with personal data such as name, lastname or DNI.
        you will retrieve this data from the message history and return it as a json with this format:
        {{
            "name": string, (optional)
            "lastname": string, (optional)
            "dni": string (optional)
        }}
        if the value is not present return null for that field.

        here is the user chat history:
        {transcription}
"""
        response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7,
                response_format={"type": "json_object"},
            )
        reply = response.choices[0].message.content
        data = json.loads(reply)
        dni = data.get('dni', None)
        name = data.get('name', None)
        lastname = data.get('lastname', None)     

        if dni:
            paciente  = Paciente.objects.filter(dni=dni).first()
            chat.patient = paciente
            chat.save()

            return f"He encontrado sus datos: Nombre: {paciente.nombre}, Apellido: {paciente.apellido}, DNI: {paciente.dni}. ¿Son correctos? Por favor responda con 'sí' o 'no'."
        elif name and lastname:
            paciente = Paciente.objects.filter(nombre__iexact=name, apellido__iexact=lastname).first()
            if paciente:
                chat.patient = paciente
                chat.save()
                return f"He encontrado sus datos: Nombre: {paciente.nombre}, Apellido: {paciente.apellido}, DNI: {paciente.dni}. ¿Son correctos? Por favor responda con 'sí' o 'no'."
            else:
                chat.current_state = 'patient_registration'
                chat.current_sub_state = 'awaiting_data'
                chat.save()
                return """No he podido encontrar sus datos. Por favor envíenos sus datos para registrarlos:
                Nombre:
                Apellido:
                DNI:
                Fecha de Nacimiento:"""

    elif chat.current_sub_state == 'awaiting_confirmation':
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

        reply = response.choices[0].message.content
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