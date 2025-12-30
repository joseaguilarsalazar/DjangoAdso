from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Cita, Paciente
from .utils.chatwoot_manager import ChatwootManager
import logging
from .tasks import send_cita_reminder
from datetime import datetime, timedelta
from django.conf import settings
from .utils.TelegramApiManager import TelegramApiManager
from .models import Cita

# Set up logging
logger = logging.getLogger(__name__)

# Configuración de Plantillas de WhatsApp
# NOTA: Asegúrate de que el orden de las variables aquí coincida EXACTAMENTE
# con el orden de {{1}}, {{2}}, {{3}} en tu administrador de WhatsApp de Meta.
TEMPLATES = {
    "notificacion_cita_medico": {
        "name": "notificacion_cita_medico", # Debe coincidir con Meta
        "category": "UTILITY",
        "language": "es"
    },
    "notificacion_cita_paciente": {
        "name": "notificacion_cita_paciente", # Debe coincidir con Meta
        "category": "UTILITY",
        "language": "es"
    },
    "encuesta_pacientes": {
        "name": "encuesta_pacientes",
        "category": "MARKETING",
        "language": "es"
    }
}

DIAS_SEMANA = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 
    4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}

@receiver(post_save, sender=Cita)
def notify_appointment_created_updated(sender, instance: Cita, created: bool, **kwargs):
    """
    Notifica a médicos y pacientes usando Plantillas de WhatsApp (Templates).
    """
    if getattr(instance, "_skip_signal", False):
        return
    
    if not instance.medico or not instance.paciente:
        logger.warning(f"Cita {instance.id} falta información de doctor o paciente")
        return
    
    doctor = instance.medico
    paciente = instance.paciente
    
    # 1. Preparar datos comunes
    dia_nombre = DIAS_SEMANA[instance.fecha.weekday()]
    fecha_formateada = instance.fecha.strftime('%d/%m/%Y')
    hora_formateada = str(instance.hora)
    
    # 2. Determinar la instancia de Chatwoot (Inbox Alias)
    # Asumimos que tu ChatwootManager maneja estos alias internamente o los mapea a IDs
    inbox_alias = 'adso_iquitos_instance' # Default
    if paciente.clinica and paciente.clinica.nomb_clin == 'Clinica Dental Filial Yurimaguas':
        inbox_alias = 'adso_instance'

    manager = ChatwootManager()

    # --- NOTIFICACIÓN AL PACIENTE (Vía Template) ---
    patient_phone = getattr(paciente, 'telf_pac', None) or getattr(paciente, 'telefono', None)
    
    if patient_phone:
        tmpl_pac = TEMPLATES["notificacion_cita_paciente"]
        
        # DEFINIR VARIABLES DEL TEMPLATE PACIENTE
        # IMPORTANTE: Ajusta este orden según tu plantilla real en Meta.
        # Ejemplo: "Hola {{1}}, su cita es el {{2}} a las {{3}} con el Dr. {{4}}"
        paciente_vars = [
            dia_nombre,       # {{1}} matches {{dia}}
            fecha_formateada, # {{2}} matches {{fecha}}
            hora_formateada,  # {{3}} matches {{hora}}
            doctor.name       # {{4}} matches {{nombre}}
        ]

        try:
            # Nota: Asegúrate de actualizar tu ChatwootManager.send_template para aceptar 'message_instance' 
            # o pasar el inbox_id correspondiente si usas múltiples inboxes.
            manager.send_template(
                number=patient_phone,
                template_name=tmpl_pac["name"],
                category=tmpl_pac["category"],
                language=tmpl_pac["language"],
                variables=paciente_vars,
                # message_instance=inbox_alias # Descomentar si modificaste send_template para aceptar esto
            )
            logger.info(f"Template enviado al paciente {paciente.id} para cita {instance.id}")
        except Exception as e:
            logger.error(f"Error enviando template paciente: {e}")
    else:
        logger.warning(f"Paciente {paciente.id} no tiene teléfono")

    # --- NOTIFICACIÓN AL DOCTOR (Vía Template) ---
    if hasattr(doctor, 'telefono') and doctor.telefono:
        tmpl_doc = TEMPLATES["notificacion_cita_medico"]
        
        # DEFINIR VARIABLES DEL TEMPLATE DOCTOR
        # Ejemplo: "Hola Dr {{1}}, tiene nueva cita con {{2}} el {{3}} a las {{4}}"
        doctor_vars = [
            doctor.name,                    # {{1}} Nombre Doctor
            str(paciente),                  # {{2}} Nombre Paciente
            f"{dia_nombre} {fecha_formateada}", # {{3}} Fecha
            hora_formateada                 # {{4}} Hora
        ]

        try:
            manager.send_template(
                number=doctor.telefono,
                template_name=tmpl_doc["name"],
                category=tmpl_doc["category"],
                language=tmpl_doc["language"],
                variables=doctor_vars,
                # message_instance=inbox_alias 
            )
            logger.info(f"Template enviado al doctor {doctor.id} para cita {instance.id}")
        except Exception as e:
            logger.error(f"Error enviando template doctor: {e}")
    else:
        logger.warning(f"Doctor {doctor.id} no tiene teléfono")


    # 3. NOTIFICACIÓN A GRUPO TELEGRAM (Texto plano)
    # Mantenemos esto igual ya que Telegram no requiere templates estrictos
    if paciente.clinica and paciente.clinica.telegram_chat_id:
        try:
            telegram_msg = f'''📅 Cita {'Creada' if created else 'Actualizada'}:
Paciente: {paciente}
Fecha: {dia_nombre} {fecha_formateada}
Hora: {hora_formateada}
Doctor: {doctor.name}'''
            
            telegram = TelegramApiManager()
            telegram.telegram_notify(
                chat_id=paciente.clinica.telegram_chat_id,
                text=telegram_msg
            )
        except Exception as e:
            logger.error(f"Error Telegram Group: {e}")

    # 4. TAREA DE RECORDATORIO (Solo al crear)
    if created:
        naive_dt = datetime.combine(instance.fecha, instance.hora)
        tz = timezone.get_current_timezone()
        cita_dt = naive_dt.replace(tzinfo=tz) if timezone.is_naive(naive_dt) else naive_dt.astimezone(tz)
        
        offset = 3 
        remind_at = cita_dt - timedelta(hours=offset)
        eta = remind_at if remind_at > timezone.now() else timezone.now() + timedelta(minutes=1)
        
        send_cita_reminder.apply_async((instance.id,), eta=eta)


@receiver(post_delete, sender=Cita)
def notify_appointment_deleted(sender, instance: Cita, **kwargs):
    """
    Notifica eliminación.
    NOTA: Se mantiene con send_message (texto) porque no se proveyó template de cancelación.
    Si la ventana de 24h está cerrada, esto fallará.
    """
    if getattr(instance, "_skip_signal", False):
        return
    if not instance.medico or not instance.paciente:
        return
    
    doctor = instance.medico
    paciente = instance.paciente
    
    dia_nombre = DIAS_SEMANA.get(instance.fecha.weekday(), 'N/A')
    fecha_formateada = instance.fecha.strftime('%d/%m/%Y')
    
    # Mensajes de texto plano (Fallback)
    mssg_pct = f"❌ Su cita del {dia_nombre} {fecha_formateada} a las {instance.hora} ha sido cancelada."
    mssg_dtr = f"❌ Cita cancelada: {paciente} - {dia_nombre} {fecha_formateada} {instance.hora}"

    # Determinar instancia
    inbox_alias = 'adso_iquitos_instance'
    if paciente.clinica and paciente.clinica.nomb_clin == 'Clinica Dental Filial Yurimaguas':
        inbox_alias = 'adso_instance'
        
    manager = ChatwootManager()
    
    # Intentar enviar al Doctor
    if hasattr(doctor, 'telefono') and doctor.telefono:
        manager.send_message(doctor.telefono, mssg_dtr, message_instance=inbox_alias)
        
    # Intentar enviar al Paciente
    patient_phone = getattr(paciente, 'telf_pac', None) or getattr(paciente, 'telefono', None)
    if patient_phone:
        manager.send_message(patient_phone, mssg_pct, message_instance=inbox_alias)