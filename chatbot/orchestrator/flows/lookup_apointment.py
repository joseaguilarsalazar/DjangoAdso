from chatbot.models import Chat
from .AI_Client import client
import json
from .trascript_history import transcript_history
from datetime import datetime, timedelta
from core.models import Cita, Paciente, Consultorio
from datetime import time

from datetime import datetime, timedelta
import unicodedata

DIAS_SEMANA = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

def normalizar_dia(dia: str) -> str:
    # minúsculas y sin espacios
    dia = dia.strip().lower()
    # quitar tildes/acentos
    dia = ''.join(
        c for c in unicodedata.normalize('NFD', dia)
        if unicodedata.category(c) != 'Mn'
    )
    return dia


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
    f{transcription}
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
    
    if not data.get('fecha_cita') and data.get('day_cita'):
        dia_normalizado = normalizar_dia(data['day_cita'])

        if dia_normalizado not in DIAS_SEMANA:
            return "No entendí el día que indicaste, ¿podrías repetirlo?"

        indice_objetivo = DIAS_SEMANA.index(dia_normalizado)
        indice_hoy = datetime.now().weekday()  # lunes=0, domingo=6

        dias_delta = (indice_objetivo - indice_hoy + 7) % 7
        fecha_cita = datetime.now() + timedelta(days=dias_delta)

    elif data.get('fecha_cita'):
        fecha_cita = datetime.strptime(data['fecha_cita'], '%Y-%m-%d')
    else:
        return "Podría por favor especificarme qué día desea agendar la cita?"


    # ------------------ NEW: calcular disponibilidad ------------------
    try:
        # usar solo la fecha
        date_obj = fecha_cita.date() if isinstance(fecha_cita, datetime) else fecha_cita

        paciente = Paciente.objects.get(id=chat.patient_id)
        consultorios_count = Consultorio.objects.filter(clinica=paciente.clinica).count() or 1

        # obtener citas de ese dia (no consideradas canceladas)
        citas_dia = Cita.objects.filter(fecha=date_obj, cancelado=False)

        # horario de trabajo (suposición): 08:00 - 20:00, intervalos de 30 minutos
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
            for s in available_slots[1:]:
                # si la diferencia es 30 minutos => consecutivo
                prev_dt = datetime.combine(date_obj, prev_slot)
                cur_dt = datetime.combine(date_obj, s)
                if (cur_dt - prev_dt) == timedelta(minutes=30):
                    prev_slot = s
                    continue
                else:
                    # cerrar intervalo (end = prev_slot + 30min)
                    end_dt = datetime.combine(date_obj, prev_slot) + timedelta(minutes=30)
                    intervals.append((start_slot, end_dt.time()))
                    start_slot = s
                    prev_slot = s
            # agregar último intervalo
            end_dt = datetime.combine(date_obj, prev_slot) + timedelta(minutes=30)
            intervals.append((start_slot, end_dt.time()))

        # formatear respuesta en español
        if not intervals:
            return "Lo siento, no hay disponibilidad ese día. ¿Desea otra fecha?"
        else:
            # Format each interval as text
            formatted = [f"de {a.strftime('%H:%M')} a {b.strftime('%H:%M')}" for a, b in intervals]

            # If there's a lot of intervals (e.g. more than 4), keep precision but summarize wording
            if len(formatted) > 4:
                short = []
                for i, (a, b) in enumerate(intervals):
                    # Merge consecutive intervals if they’re close (e.g. <15 min apart)
                    if i == 0:
                        start = a
                        end = b
                    else:
                        prev_end = intervals[i-1][1]
                        # merge small gaps
                        if (a - prev_end).total_seconds() / 60 <= 15:
                            end = b
                        else:
                            short.append((start, end))
                            start, end = a, b
                short.append((start, end))
                formatted = [f"de {a.strftime('%H:%M')} a {b.strftime('%H:%M')}" for a, b in short]

            # Build the natural-language sentence
            if len(formatted) == 1:
                disponibilidad = formatted[0]
            else:
                disponibilidad = " y ".join(formatted[:-1]) + " y " + formatted[-1]

            data = {
                'fecha_cita': date_obj.strftime('%Y-%m-%d')
            }

            chat.current_state = "register_appointment"
            chat.save()
            return f"Atendemos ese día y tenemos disponibilidad {disponibilidad}."
    except Paciente.DoesNotExist:
        chat.current_state = 'data_confirmation'
        chat.save()
        return "Podria darme su dni para verificar su informacion?"
    except ValueError:
        return "No pude interpretar la fecha solicitada. ¿Podría indicarla en formato YYYY-MM-DD?"
    except Exception:
        chat.current_state = "lookup_appointment"
        chat.save()

        return "Ocurrió un error al consultar la disponibilidad. Por favor intente más tarde."