from chatbot.models import Chat
from .AI_Client import client
from .trascript_history import transcript_history
from core.models import Cita, Paciente, Consultorio
import json
from datetime import datetime, timedelta

# --- UPDATED IMPORT ---
from .dayParser import DayNormalizer 

# Initialize the normalizer
normalizer = DayNormalizer()

def register_appointment(messages, chat: Chat):
    transcription, history = transcript_history(messages)

    if not chat.patient:
        chat.current_state = "patient_registration"
        chat.current_sub_state = "awaiting_data"
        chat.save()
        return """Por favor bríndeme estos datos antes de registrar una cita:
        Nombre:
        Apellido:
        DNI:
        Fecha de Nacimiento:
        Ciudad de residencia (Iquitos o Yurimaguas):
        """

    prompt = f"""
    Estás recibiendo la historia de chat de un paciente que desea registrar una cita en la clínica dental.
    Basado en los datos del chat (especialmente los últimos mensajes) extrae la siguiente información en formato json:
    {{
        'day_cita': string, # e.g. lunes, martes, miercoles, jueves, viernes, sabado, domingo
        'fecha_cita': string, # formato YYYY-MM-DD solo si es posible extraerlo de lo contrario null
        'hora_cita': string, # formato HH:MM
    }}

    Aquí la historia del chat:
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
    
    fecha_cita = None

    # ------------------ LOGIC UPDATE START ------------------
    if not data.get('fecha_cita') and data.get('day_cita'):
        # 1. Check if we already calculated the date in a previous step (lookup_appointment)
        if chat.extra_data and chat.extra_data.get('fecha_cita'):
            fecha_cita = datetime.strptime(chat.extra_data['fecha_cita'], '%Y-%m-%d')
            # Clear extra data after using it
            chat.extra_data = {} 
            chat.save()
        else:
            # 2. Calculate date using DayNormalizer
            dia_normalizado = normalizer.normalize(data['day_cita'])
            
            if not dia_normalizado:
                return "No entendí el día para la cita. ¿Podría repetirlo?"

            target_idx = normalizer.CANONICAL_DAYS.index(dia_normalizado)
            current_idx = datetime.now().weekday()
            
            # Calculate days until target day
            delta = (target_idx - current_idx + 7) % 7
            
            # If user says "Monday" and today is "Monday", assume next week (7 days) 
            # instead of today (0 days), unless you prefer today.
            if delta == 0: 
                delta = 7
                
            fecha_cita = datetime.now() + timedelta(days=delta)

    elif data.get('fecha_cita'):
        fecha_cita = datetime.strptime(data['fecha_cita'], '%Y-%m-%d')
    else:
        # Fixed typo in state name: 'lookup_apointmnet' -> 'lookup_appointment'
        chat.current_state = "lookup_appointment" 
        chat.save()
        return "Podría por favor especificarme qué día desea agendar la cita?"
    # ------------------ LOGIC UPDATE END ------------------

    
    # Corrección de fecha: Asegurar que fecha_cita no tenga horas/minutos residuales
    if isinstance(fecha_cita, datetime):
        fecha_cita = fecha_cita.date() 

    paciente = Paciente.objects.get(id=chat.patient_id)
    consultorios = Consultorio.objects.filter(clinica=paciente.clinica).order_by('id')
    
    consultorio_disponible = None 

    for consultorio in consultorios:
        citas_existentes = Cita.objects.filter(
            consultorio=consultorio,
            fecha=fecha_cita, 
            hora=data.get('hora_cita') # Safely get hora
        )
        if not citas_existentes.exists():
            consultorio_disponible = consultorio
            break 
    
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
        cita.fecha.strftime('%Y-%m-%d'), cita.hora)