from chatbot.models import Chat
from .AI_Client import client
from .trascript_history import transcript_history
from core.models import Cita, Paciente
import json
from datetime import datetime, timedelta

def register_appointment(messages, chat: Chat):
    transcription, history = transcript_history(messages)

    prompt = f"""
    Estas recibiendo la hisotia de chat de un paciente que desea registrar una cita en la clinica dental.
    basado en los datos del chat (especialmente los ultimos mensajes) extrae la siguiente informacion en formato json:
    {{
        'day_cita': string, # e.g. lunes, martes, miercoles, jueves, viernes, sabado, domingo
        'fecha_cita': string, # formato YYYY-MM-DD solo si es posible extraerlo de lo contrario null
        'hora_cita': string, # formato HH:MM
    }}

    Aqui la historia del chat:
    {transcription}
"""
    ai_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7,
                response_format={"type": "json_object"},
    )

    if not ai_response.choices:
        return "Lo siento, no pude registrar su cita. Por favor intente nuevamente."
    ai_reply = ai_response.choices[0].message.content
    data = json.loads(ai_reply)
    if data['hora_cita']:
        return "Podria confirmarme a que hora desa agendar la cita?"
    
    if not data['fecha_cita'] and data['day_cita']:
        #Establece la cita en el proximo dia de semana especificado
        fecha_cita = datetime.now() + timedelta((list(['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']).index(data['day_cita'].lower()) - datetime.now().weekday() + 7) % 7)
    elif data['fecha_cita']:
        fecha_cita = datetime.strptime(data['fecha_cita'], '%Y-%m-%d')
    else:
        return "Podria por favor especificarme que dia desea agendar la cita?"

    paciente = Paciente.objects.get(id=chat.paciente_id)
    cita = Cita.objects.create(
        paciente=paciente,
        fecha=fecha_cita,
        hora=data['hora_cita']
    )
    return 'Cita registrada'