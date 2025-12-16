from celery import shared_task
from .models import Cita, Clinica
from .utils.chatwoot_manager import ChatwootManager
from .utils.TelegramApiManager import TelegramApiManager
from datetime import date, timedelta

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