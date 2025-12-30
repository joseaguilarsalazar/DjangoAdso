from celery import shared_task
from .models import Cita, Clinica
from .utils.chatwoot_manager import ChatwootManager
from .utils.TelegramApiManager import TelegramApiManager
from datetime import date, timedelta
from .models import Paciente
import logging
import time
from chatbot.models import Chat

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
def enviar_encuesta_masiva_task(target_number=None):
    """
    Envía el template de encuesta a todos los pacientes únicos.
    Si target_number está presente, filtra solo ese número para testing.
    """
    manager = ChatwootManager()
    
    # 1. Base Query: Obtener pacientes con teléfono válido
    pacientes = Paciente.objects.exclude(telf_pac__isnull=True).exclude(telf_pac__exact='').select_related('clinica')
    
    # --- MODIFICACIÓN: FILTRO DE MODO TEST ---
    if target_number:
        # Si recibimos un número, filtramos el QuerySet para traer SOLO ese paciente.
        # Usamos icontains por si el input es "999888777" pero en DB está como "999 888 777"
        # (Aunque lo ideal es que coincida exacto, esto ayuda en testing)
        pacientes = pacientes.filter(telf_pac__icontains=target_number)
        if pacientes.count() == 0:
            new_paciente = Paciente(telf_pac=target_number, nomb_pac="Test", apel_pac="Paciente", clinica_id=1)
            new_paciente.save()
            pacientes = Paciente.objects.filter(id=new_paciente.id)
        logger.info(f"🧪 MODO TEST ACTIVADO: Buscando coincidencias para '{target_number}'")
    else:
        logger.info(f"🚀 Iniciando campaña masiva de encuestas a {pacientes.count()} candidatos potenciales.")

    mensajes_enviados = 0
    numeros_procesados = set() 
    errores = 0

    if not pacientes.exists() and target_number:
        logger.warning(f"⚠️ MODO TEST: No se encontró ningún paciente con el número {target_number}")
        return "Modo Test: Número no encontrado en DB."

    for paciente in pacientes:
        # Normalizar teléfono
        telefono = str(paciente.telf_pac).strip().replace(' ', '')
        
        # --- LÓGICA DE DEDUPLICACIÓN ---
        if telefono in numeros_procesados:
            continue 
        
        numeros_procesados.add(telefono)

        # --- SELECCIÓN DE INBOX ---
        inbox_alias = 'adso_iquitos_instance' 
        if paciente.clinica and paciente.clinica.nomb_clin == 'Clinica Dental Filial Yurimaguas':
            inbox_alias = 'adso_instance'

        # --- PREPARACIÓN DE VARIABLES ---
        variables = [paciente.nomb_pac.split()[0]] if paciente.nomb_pac else ["Paciente"]

        try:
            # Enviar Template
            manager.send_template(
                number=telefono,
                template_name=ENCUESTA_TEMPLATE["name"],
                category=ENCUESTA_TEMPLATE["category"],
                language=ENCUESTA_TEMPLATE["language"],
                variables=variables,
            )
            mensajes_enviados += 1

            # Buscar o crear Chat para rastrear estado
            chat = Chat.objects.filter(number=telefono).first()
            if not chat:
                chat = Chat.objects.create(number=telefono)
            
            chat.current_state = "esperando_encuesta"
            chat.save()

            # ⚠️ Rate Limiting (Solo si es masivo, en test no es tan critico pero no hace daño)
            time.sleep(0.5) 

        except Exception as e:
            logger.error(f"❌ Error enviando a {telefono}: {e}")
            errores += 1

    logger.info(f"🏁 Finalizado. Enviados: {mensajes_enviados}. Errores: {errores}. Mode: {'TEST' if target_number else 'MASIVO'}")
    return f"Mode: {'TEST' if target_number else 'BROADCAST'} | Enviados: {mensajes_enviados}, Errores: {errores}"