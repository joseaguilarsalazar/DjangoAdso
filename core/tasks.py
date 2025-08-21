from celery import shared_task
from .models import Cita
from .utils.EvolutionApiManager import EvolutionApiManager  # your class

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

    evo = EvolutionApiManager()
    state = evo.check_instance_state()
    if state.get.get("state") not in {"open", "connected"}:
        # Retry later if instance not ready
        raise self.retry(exc=RuntimeError("Instance not connected"))

    # Build numbers (tweak to your fields)
    medico_num = f"51{cita.medico.telefono}" if cita.medico and cita.medico.telefono else None
    paciente_num = f"51{getattr(cita.paciente, 'telf_pac', '')}" if cita.paciente and getattr(cita.paciente, "telf_pac", None) else None

    fecha = cita.fecha.strftime("%Y-%m-%d")
    hora  = cita.hora.strftime("%H:%M")
    msg   = f"⏰ Recordatorio: su CITA es hoy {fecha} a las {hora}."

    if medico_num:
        evo.send_message(medico_num, f"{msg} (Médico)")
    if paciente_num:
        evo.send_message(paciente_num, f"{msg} (Paciente)")

    cita.reminder_sent = True

    return "OK"
