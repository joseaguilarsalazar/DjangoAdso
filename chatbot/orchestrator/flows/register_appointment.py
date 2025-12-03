from chatbot.models import Chat
from .AI_Client import client
from .trascript_history import transcript_history
from core.models import Cita, Paciente, Consultorio
import json
from datetime import datetime, timedelta

def register_appointment(messages, chat: Chat):
    transcription, history = transcript_history(messages)

    if not chat.patient:
        chat.current_state = "patient_registration"
        chat.current_sub_state = "awaiting_data"
        chat.save()
        return """Por favor brindeme estos datos antes de registrar una cita:
        Nombre:
        Apellido:
        DNI:
        Fecha de Nacimiento:
        Ciudad de residencia (Iquitos o Yurimaguas):
        """

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
    
    if not data['fecha_cita'] and data['day_cita']:
        if chat.extra_data and chat.extra_data.get('fecha_cita', None):
            fecha_cita = chat.extra_data['fecha_cita']
            chat.extra_data = {}
            chat.save()

        #Establece la cita en el proximo dia de semana especificado
        else:
            fecha_cita = datetime.now() + timedelta((list(['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']).index(data['day_cita'].lower()) - datetime.now().weekday() + 7) % 7)
    elif data['fecha_cita']:
        fecha_cita = datetime.strptime(data['fecha_cita'], '%Y-%m-%d')
    else:
        chat.current_state = "lookup_apointmnet"
        chat.save()
        return "Podria por favor especificarme que dia desea agendar la cita?"

    
    # Corrección de fecha: Asegurar que fecha_cita no tenga horas/minutos residuales
    # Si calculaste fecha_cita con datetime.now(), conviértelo a date puro
    if isinstance(fecha_cita, datetime):
        fecha_cita = fecha_cita.date() 

    paciente = Paciente.objects.get(id=chat.patient_id)
    consultorios = Consultorio.objects.filter(clinica=paciente.clinica).order_by('id')
    
    consultorio_disponible = None # Variable bandera

    for consultorio in consultorios:
        citas_existentes = Cita.objects.filter(
            consultorio=consultorio,
            fecha=fecha_cita, # Ya es un objeto date puro
            hora=data['hora_cita']
        )
        if not citas_existentes.exists():
            consultorio_disponible = consultorio
            break # Encontramos uno libre, salimos y guardamos la referencia
    
    # VERIFICACIÓN CRÍTICA
    if not consultorio_disponible:
        return "Lo siento, no hay consultorios disponibles en ese horario. ¿Podría intentar otra hora?"

    # Crear la cita con el consultorio que sí está libre
    cita = Cita.objects.create(
        paciente=paciente,
        consultorio=consultorio_disponible,
        fecha=fecha_cita,
        hora=data['hora_cita']
    )
    
    return """Su cita ha sido registrada exitosamente para el día {} a las {}.""".format(
        cita.fecha.strftime('%Y-%m-%d'), cita.hora) # cita.hora ya suele ser string o time object