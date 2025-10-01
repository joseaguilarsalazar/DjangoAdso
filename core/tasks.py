from celery import shared_task
from .models import Cita
from .utils.EvolutionApiManager import EvolutionApiManager
from .utils.TelegramApiManager import TelegramApiManager
import requests

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

    if medico_num:
        evo.send_message(medico_num, f"{msg} (Médico)")
    if paciente_num:
        evo.send_message(paciente_num, f"{msg} (Paciente)")

    cita.reminder_sent = True

    return "OK"


@shared_task(bind=True, autoretry_for=(requests.RequestException,),
             retry_backoff=True, retry_kwargs={"max_retries": 3})
def check_evolution_and_notify(self):
    """
    Runs every 15 minutes via beat. If instance is not connected, send Telegram alert.
    """
    evo = EvolutionApiManager()
    tele = TelegramApiManager()
    data = evo.check_instance_state()

    # Normalize whatever your API returns. Common fields: "state": "open|connecting|close"
    state = (data.get("instance") or {}).get("state") or data.get("state")
    ok_states = {"open", "connected", "online"}  # include your API's "healthy" value(s)

    if state not in ok_states:
        tele.telegram_notify(
            f"⚠️ Evolution API instance adso_iquitos_instance is *{state or 'unknown'}*."
        )
    return {"state": state}