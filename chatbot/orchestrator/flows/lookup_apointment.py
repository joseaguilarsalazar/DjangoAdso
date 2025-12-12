from chatbot.models import Chat
from .AI_Client import client
import json
from .trascript_history import transcript_history
from datetime import datetime, timedelta, time
from core.models import Cita, Paciente, Consultorio

# --- NEW IMPORT ---
# Change '.utils' to the actual name of the file where you put the class
from .dayParser import DayNormalizer 

# Initialize the normalizer once
normalizer = DayNormalizer()

def lookup_appointment(messages, chat: Chat):
    transcription, history = transcript_history(messages)
    
    prompt = f"""
    Eres un asistente que debe detectar si en el historial de mensajes dado, el paciente especifica
    que dia exactamente le gustaria agendar una cita, en el siguiente formato json:
    {{
        'fecha_cita': string, # formato YYYY-MM-DD
                        or
        'day_cita': string, # e.g. lunes, martes, miercoles, jueves, viernes, sabado, domingo
    }}
    solo uno de los dos es necesario, procura que sea fecha_cita si es posible extraerla.
    Si no es posible extraer ninguno de los dos, responde con:
    {{
        'fecha_cita': null,
        'day_cita': null
    }}
    Aqui la historia del chat, si hay mas de 2 fechas mencionadas para citas, elige la ultima mencionada:
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
        return "Lo siento, no pude entender su solicitud. Por favor intente nuevamente."
    
    data = json.loads(ai_response.choices[0].message.content)
    
    # ------------------ LOGIC UPDATE START ------------------
    if not data.get('fecha_cita') and data.get('day_cita'):
        # Use the class method instead of the old function
        dia_normalizado = normalizer.normalize(data['day_cita'])

        # If normalize returns None, it wasn't a valid day
        if not dia_normalizado:
            return "No entendí el día que indicaste, ¿podrías repetirlo?"

        # Use the list inside the class to find the index
        days_list = normalizer.CANONICAL_DAYS 
        indice_objetivo = days_list.index(dia_normalizado)
        
        indice_hoy = datetime.now().weekday()  # lunes=0, domingo=6

        dias_delta = (indice_objetivo - indice_hoy + 7) % 7
        # If delta is 0, it means the user said "Monday" and today is Monday.
        # Usually, this implies "Next Monday" (7 days later), not today.
        # If you want it to be today, keep it as is. If you want next week:
        if dias_delta == 0:
             dias_delta = 7

        fecha_cita = datetime.now() + timedelta(days=dias_delta)

    elif data.get('fecha_cita'):
        fecha_cita = datetime.strptime(data['fecha_cita'], '%Y-%m-%d')
    else:
        return "Podría por favor especificarme qué día desea agendar la cita?"
    # ------------------ LOGIC UPDATE END ------------------


    # ------------------ CALCULAR DISPONIBILIDAD ------------------
    try:
        # usar solo la fecha
        date_obj = fecha_cita.date() if isinstance(fecha_cita, datetime) else fecha_cita

        paciente = Paciente.objects.get(id=chat.patient_id)
        consultorios_count = Consultorio.objects.filter(clinica=paciente.clinica).count() or 1

        # obtener citas de ese dia (no consideradas canceladas)
        citas_dia = Cita.objects.filter(fecha=date_obj, cancelado=False)

        # horario de trabajo: 08:00 - 20:00
        inicio = datetime.combine(date_obj, time(hour=8, minute=0))
        fin = datetime.combine(date_obj, time(hour=20, minute=0))

        slots = []
        cur = inicio
        while cur < fin:
            slots.append(cur.time())
            cur += timedelta(minutes=30)

        available_slots = []
        for slot in slots:
            ocupadas = citas_dia.filter(hora=slot).count()
            if ocupadas < consultorios_count:
                available_slots.append(slot)

        # agrupar slots consecutivos en intervalos
        intervals = []
        if available_slots:
            start_slot = available_slots[0]
            prev_slot = start_slot
            
            # Helper to calculate difference between times (handling date wrapping)
            def get_diff_mins(t1, t2):
                d1 = datetime.combine(date_obj, t1)
                d2 = datetime.combine(date_obj, t2)
                return (d1 - d2).total_seconds() / 60

            for s in available_slots[1:]:
                # si la diferencia es 30 minutos => consecutivo
                if get_diff_mins(s, prev_slot) == 30:
                    prev_slot = s
                    continue
                else:
                    # cerrar intervalo
                    end_dt = datetime.combine(date_obj, prev_slot) + timedelta(minutes=30)
                    intervals.append((start_slot, end_dt.time()))
                    start_slot = s
                    prev_slot = s
            
            # agregar último intervalo
            end_dt = datetime.combine(date_obj, prev_slot) + timedelta(minutes=30)
            intervals.append((start_slot, end_dt.time()))

        # formatear respuesta
        if not intervals:
            return "Lo siento, no hay disponibilidad ese día. ¿Desea otra fecha?"
        else:
            # First format pass
            formatted_intervals = []
            
            # Logic to merge small gaps or just list them
            # Note: I simplified the complex merging logic slightly to prevent TypeError 
            # when subtracting 'time' objects directly.
            
            for start, end in intervals:
                formatted_intervals.append(f"de {start.strftime('%H:%M')} a {end.strftime('%H:%M')}")

            # Natural language join
            if len(formatted_intervals) == 1:
                disponibilidad = formatted_intervals[0]
            else:
                disponibilidad = ", ".join(formatted_intervals[:-1]) + " y " + formatted_intervals[-1]

            data = {
                'fecha_cita': date_obj.strftime('%Y-%m-%d'),
            }
            chat.extra_data = data
            chat.current_state = "register_appointment"
            chat.save()
            
            return f"Atendemos ese día y tenemos disponibilidad {disponibilidad}."

    except Paciente.DoesNotExist:
        chat.current_state = 'data_confirmation'
        chat.save()
        return "Podria darme su dni para verificar su informacion?"
    except ValueError:
        return "No pude interpretar la fecha solicitada. ¿Podría indicarla en formato YYYY-MM-DD?"
    except Exception as e:
        print(f"Error fetching availability: {e}") # Log error for debugging
        chat.current_state = "lookup_appointment"
        chat.save()
        return "Ocurrió un error al consultar la disponibilidad. Por favor intente más tarde."