from chatbot.models import Chat
from .AI_Client import client
import json
from .trascript_history import transcript_history

def data_confirmation(messages, chat: Chat):
    transcription, history = transcript_history(messages)
    if chat.current_sub_state == 'default':
        #the user gives dni, name or lastname to confirm data use ai to retrieve patient data
        #and then confirm it in the database in the Paciente model
        #if user exists send to user and pass to awaiting_confirmation
        #else ask for registration
        pass

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