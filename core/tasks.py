from celery import shared_task
from .models import Cita, Clinica
from chatbot.models import Chat
from .utils.chatwoot_manager import ChatwootManager
from .utils.TelegramApiManager import TelegramApiManager
from datetime import date, timedelta
from .models import Paciente
import logging
import time
from chatbot.models import Chat, Message, EncuestaSatisfaccion
from core.utils.whatsapp_manager import WhatsAppManager
from chatbot.orchestrator.flows.AI_Client import client
from chatbot.orchestrator.flows.trascript_history import transcript_history
import json

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_cita_reminder(self, cita_id: int):
    try:
        cita = Cita.objects.select_related("paciente", "medico").get(pk=cita_id)
    except Cita.DoesNotExist:
        return "Cita no existe"

    # (Optional) skip if cita was cancelled or already completed
    if getattr(cita, "estadoCita", None) in {"CANCELADA", "COMPLETADA"}:
        return "Saltado por estado"
    
    if cita.reminder_sent == True:
        return 'Salatando, mesaje ya mandado'

    chatwoot = ChatwootManager()
    state = chatwoot.check_instance_state()
    print(state)
    if state.get("state") not in {"open", "connected"}:
        # Retry later if instance not ready
        raise self.retry(exc=RuntimeError("Instance not connected"))

    # Build numbers (tweak to your fields)
    medico_num = f"51{cita.medico.telefono}" if cita.medico and cita.medico.telefono else None
    paciente_num = f"51{getattr(cita.paciente, 'telf_pac', '')}" if cita.paciente and getattr(cita.paciente, "telf_pac", None) else None

    fecha = cita.fecha.strftime("%Y-%m-%d")
    hora  = cita.hora.strftime("%H:%M")
    msg   = f"⏰ Recordatorio: su CITA es hoy {fecha} a las {hora}."

    if paciente_num:
        chatwoot.send_message(paciente_num, f"{msg} (Paciente)")

    if cita.medico:
        parte_mensaje = f"Con el odontologo/a {cita.medico.first_name} {cita.medico.last_name}."
    else:
        parte_mensaje = "Sin Odontologo asignado."

    if cita.paciente.clinica.telegram_chat_id:
        telegram = TelegramApiManager()
        telegram.telegram_notify(
            chat_id=cita.paciente.clinica.telegram_chat_id,
            text=f"""Se registro una cita para el paciente {cita.paciente.nombre_pac} {cita.paciente.apellido_pac} el dia {fecha} a las {hora}.
                    {parte_mensaje}"""
        )


    cita.reminder_sent = True

    return "OK"

@shared_task
def send_daily_report():
    clinicas = Clinica.objects.all()
    telegram = TelegramApiManager()
    for clinica in clinicas:
        if not clinica.telegram_chat_id:
            continue
        
        apointments_registered_today = Cita.objects.filter(clinica=clinica, created_at=date.today())
        appointments_for_tomorrow_count = apointments_registered_today.filter(fecha=date.today() + timedelta(days=1)).count()
        appointments_with_no_doctor = apointments_registered_today.filter(medico__isnull=True).count()

        reporte = f"""Reporte Diario de Citas - {date.today().strftime("%Y-%m-%d")}
Total de citas registradas hoy: {apointments_registered_today.count()}
Citas programadas para mañana: {appointments_for_tomorrow_count}
Citas sin odontólogo asignado: {appointments_with_no_doctor}
Esta es la lista detallada de citas registradas hoy:\n"""
        
        for cita in apointments_registered_today:
            fecha = cita.fecha.strftime("%Y-%m-%d")
            hora  = cita.hora.strftime("%H:%M")
            paciente = f"{cita.paciente.nombre_pac} {cita.paciente.apellido_pac}"
            medico = f"{cita.medico.first_name} {cita.medico.last_name}" if cita.medico else "N/A"
            reporte += f"\n- Paciente: {paciente}, Fecha: {fecha}, Hora: {hora}, Odontólogo: {medico if medico else 'N/A'}"

        telegram.telegram_notify(
            chat_id=clinica.telegram_chat_id,
            text=reporte
        )

ENCUESTA_TEMPLATE = {
    "name": "encuesta_pacientes",
    "category": "MARKETING",
    "language": "es"
}

@shared_task
def enviar_encuesta_masiva_task(target_number=None, year=None):
    """
    Envía el template de encuesta a todos los pacientes únicos usando la API Directa de Meta.
    """
    # 1. Instanciar el nuevo cliente directo
    client = WhatsAppManager()
    
    # 2. Base Query
    pacientes = Paciente.objects.exclude(telf_pac__isnull=True).exclude(telf_pac__exact='')
    
    # --- FILTRO DE MODO TEST ---
    if target_number:
        pacientes = pacientes.filter(telf_pac__icontains=target_number)
        
        # Si no existe en DB, creamos uno temporal para probar
        if pacientes.count() == 0:
            logger.info(f"🧪 Creando paciente dummy para test: {target_number}")
            new_paciente = Paciente(telf_pac=target_number, nomb_pac="Test", apel_pac="Paciente", clinica_id=1)
            new_paciente.save()
            pacientes = Paciente.objects.filter(id=new_paciente.id)
            
        logger.info(f"🧪 MODO TEST ACTIVADO: Enviando a '{target_number}'")
    else:
        logger.info(f"🚀 Iniciando campaña masiva a {pacientes.count()} pacientes.")

    if year:
        pacientes = pacientes.filter(cita__fecha__year=year).distinct()
        
        logger.info(f"📅 Filtro por año {year} aplicado. Pacientes restantes: {pacientes.count()}")

    mensajes_enviados = 0
    numeros_procesados = set() 
    errores = 0

    if not pacientes.exists() and target_number:
        return "Modo Test: Error generando paciente."

    for paciente in pacientes:
        # Normalizar teléfono
        raw_phone = str(paciente.telf_pac).strip().replace(' ', '')
        
        # --- FIX IMPORTANTE PARA META API ---
        # Meta requiere el código de país (51) sin el símbolo '+'.
        # Si el número tiene 9 dígitos (celular Perú), le agregamos 51.
        if len(raw_phone) == 9:
            telefono = f"51{raw_phone}"
        elif raw_phone.startswith('+'):
            telefono = raw_phone.replace('+', '')
        else:
            telefono = raw_phone

        # --- LÓGICA DE DEDUPLICACIÓN ---
        if telefono in numeros_procesados:
            continue 
        
        numeros_procesados.add(telefono)

        try:
            # --- NUEVA LÓGICA DE ENVÍO DIRECTO ---
            # Como el template es texto plano, enviamos components vacío list []
            # Si tuvieras variables en el futuro, usarías: client.build_components(...)
            resp = client.send_template(
                to_number=telefono,
                template_name=ENCUESTA_TEMPLATE["name"],
                language_code=ENCUESTA_TEMPLATE["language"],
                components=[] 
            )

            if resp['ok']:
                mensajes_enviados += 1
                
                # --- ACTUALIZACIÓN DE ESTADO LOCAL ---
                # Seguimos usando tu modelo Chat para saber a quién se le envió
                chat = Chat.objects.filter(number=telefono).first()
                if not chat:
                    chat = Chat.objects.create(number=telefono)

                new_message = Message.objects.create(
                    chat=chat,
                    text = """Hola,
Esperamos que te encuentres muy bien.

En nuestra clínica valoramos mucho la confianza que nos brindaste este año al cuidar tu salud dental. Por eso, queremos seguir mejorando para ti y para cada uno de nuestros pacientes.

Si deseas, nos encantaría que nos regales un breve comentario:
* ¿Qué fue lo que más valoraste de nuestra atención?
* ¿Hay algo que crees que podríamos mejorar?
* ¿O alguna sugerencia para nuestro equipo?

Tu opinión es muy importante para nosotros y nos ayuda a seguir creciendo y brindándote una atención cada vez más cercana y de calidad.

¡Muchas gracias por ser parte de nuestra familia dental""",
                    from_user=False,
                    )
                
                chat.current_state = "esperando_encuesta"
                chat.save()
            else:
                logger.error(f"❌ Meta rechazó el mensaje a {telefono}: {resp.get('error')}")
                errores += 1

            # Rate Limiting (Meta permite hasta 80 mensajes/seg, pero 0.1s es seguro y amable)
            time.sleep(0.1) 

        except Exception as e:
            logger.error(f"❌ Excepción enviando a {telefono}: {e}")
            errores += 1

    logger.info(f"🏁 Finalizado. Enviados: {mensajes_enviados}. Errores: {errores}. Mode: {'TEST' if target_number else 'MASIVO'}")
    return f"Mode: {'TEST' if target_number else 'BROADCAST'} | Enviados: {mensajes_enviados}, Errores: {errores}"
    
    


@shared_task
def analyze_survey_responses_task(target_number=None, year=None):

    ENCUESTA_TEXT = """Esperamos que te encuentres muy bien.

        En nuestra clínica valoramos mucho la confianza que nos brindaste este año al cuidar tu salud dental. Por eso, queremos seguir mejorando para ti y para cada uno de nuestros pacientes.

        Si deseas, nos encantaría que nos regales un breve comentario:
        • ¿Qué fue lo que más valoraste de nuestra atención?
        • ¿Hay algo que crees que podríamos mejorar?
        • ¿O alguna sugerencia para nuestro equipo?

        Tu opinión es muy importante para nosotros y nos ayuda a seguir creciendo y brindándote una atención cada vez más cercana y de calidad.

        ¡Muchas gracias por ser parte de nuestra familia dental!"""
    # 1. Base Query
    pacientes = Paciente.objects.exclude(telf_pac__isnull=True).exclude(telf_pac__exact='')

    # --- FILTERS ---
    if target_number:
        pacientes = pacientes.filter(telf_pac__icontains=target_number)
        if not pacientes.exists():
            logger.info(f"🧪 Creando paciente dummy: {target_number}")
            new_paciente = Paciente.objects.create(telf_pac=target_number, nomb_pac="Test", apel_pac="User", clinica_id=1)
            pacientes = Paciente.objects.filter(id=new_paciente.id)
    
    if year:
        pacientes = pacientes.filter(cita__fecha__year=year).distinct()

    logger.info(f"🚀 Starting AI Analysis for {pacientes.count()} patients.")
    processed = 0

    for patient in pacientes:
        try:
            # 2. Robust Phone Matching
            clean_phone = str(patient.telf_pac).strip().replace(' ', '').replace('+', '')
            # Try exact match first, then contains
            chat = Chat.objects.filter(number__icontains=clean_phone).first()
            
            if not chat:
                continue

            # 3. Get History
            # Ensure we get enough context. Adjust limit if necessary.
            messages = chat.last_messages(limit=15) 
            
            # Optimization: If only 1 message (the survey itself) or empty, skip LLM
            if len(messages) < 2: 
                continue

            # Assuming transcript_history returns (text, list)
            transcript_text, _ = transcript_history(messages)

            # 4. Improved Prompt
            prompt = f"""
            You are a Data Analyst for a Dental Clinic. Analyze the chat history to find the patient's response to this survey:
            "{ENCUESTA_TEXT}"

            Chat History:
            {transcript_text}

            Determine if the patient actually answered the survey or provided relevant feedback.
            If they only talked about appointments/scheduling/unrelated topics, set "is_relevant": false.

            Return JSON:
            {{
                "is_relevant": boolean, 
                "main_sentiment": "POSITIVE" | "NEUTRAL" | "NEGATIVE",
                "positive_points": "string summary",
                "improvement_areas": "string summary",
                "suggestions": "string summary"
            }}
            """

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=350,
                temperature=0.0, # Lower temperature for analytical tasks
                response_format={"type": "json_object"},
            )

            # 5. Robust Parsing
            content = response.choices[0].message.content
            # Fix common LLM markdown issue
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "")
            
            data = json.loads(content)

            # 6. Only Save if Relevant
            if data.get("is_relevant", False):
                EncuestaSatisfaccion.objects.update_or_create(
                    paciente=patient,
                    defaults={
                        "sentimiento": data.get("main_sentiment", "NEUTRAL"),
                        "aspectos_positivos": data.get("positive_points", ""),
                        "areas_mejora": data.get("improvement_areas", ""),
                        "sugerencias": data.get("suggestions", ""),
                        "texto_original": transcript_text[-1000:], # Save just the last part to save space
                    }
                )
                processed += 1
                logger.info(f"✅ Feedback saved for {patient.id}")
            else:
                logger.info(f"ℹ️ Irrelevant chat for {patient.id}")

        except Exception as e:
            logger.error(f"❌ Error analyzing patient {patient.id}: {e}")
            continue

    return f"Analysis finished. Processed {processed} relevant responses."