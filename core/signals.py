from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Cita
from .utils.EvolutionApiManager import EvolutionApiManager
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Spanish day names mapping
DIAS_SEMANA = {
    0: 'Lunes',
    1: 'Martes', 
    2: 'Miércoles',
    3: 'Jueves',
    4: 'Viernes',
    5: 'Sábado',
    6: 'Domingo'
}

@receiver(post_save, sender=Cita)
def notify_appointment_created_updated(sender, instance: Cita, created: bool, **kwargs):
    """
    Notify medics and patients when an appointment is created or updated
    """
    if not instance.medico or not instance.paciente:
        logger.warning(f"Appointment {instance.id} missing doctor or patient information")
        return
    
    doctor = instance.medico
    paciente = instance.paciente
    
    # Get day name in Spanish
    dia_nombre = DIAS_SEMANA.get(instance.fecha.weekday(), 'N/A')
    
    # Format date properly
    fecha_formateada = instance.fecha.strftime('%d/%m/%Y')
    
    # Create messages based on action
    if created:
        # New appointment created
        mssg_pct = f'''✅ Se ha programado su cita para el día {dia_nombre}
{fecha_formateada} a las {instance.hora}.
Doctor: {doctor.name}'''
        
        mssg_dtr = f'''📅 Nueva cita programada:
Paciente: {paciente.__str__()}
Fecha: {dia_nombre} {fecha_formateada}
Hora: {instance.hora}'''
    else:
        # Appointment updated
        mssg_pct = f'''📝 Su cita ha sido reprogramada para el día {dia_nombre}
{fecha_formateada} a las {instance.hora}.
Doctor: {doctor.name}'''
        
        mssg_dtr = f'''📝 Cita actualizada:
Paciente: {paciente.__str__()}
Nueva fecha: {dia_nombre} {fecha_formateada}
Nueva hora: {instance.hora}'''
    
    # Send messages
    _send_notifications(doctor, paciente, mssg_dtr, mssg_pct, instance.id, "created/updated")

@receiver(post_delete, sender=Cita)
def notify_appointment_deleted(sender, instance: Cita, **kwargs):
    """
    Notify medics and patients when an appointment is deleted
    """
    if not instance.medico or not instance.paciente:
        logger.warning(f"Deleted appointment missing doctor or patient information")
        return
    
    doctor = instance.medico
    paciente = instance.paciente
    
    # Get day name in Spanish
    dia_nombre = DIAS_SEMANA.get(instance.fecha.weekday(), 'N/A')
    fecha_formateada = instance.fecha.strftime('%d/%m/%Y')
    
    # Cancellation messages
    mssg_pct = f'''❌ Su cita del día {dia_nombre} {fecha_formateada}
               a las {instance.hora} ha sido cancelada.
               Por favor contacte al consultorio si quisiera reprogramar.'''
    
    mssg_dtr = f'''❌ Cita cancelada:
               Paciente: {paciente.__str__()}
               Fecha: {dia_nombre} {fecha_formateada}
               Hora: {instance.hora}'''
    
    # Send messages
    _send_notifications(doctor, paciente, mssg_dtr, mssg_pct, instance.id, "deleted")

def _send_notifications(doctor, paciente, mssg_dtr: str, mssg_pct: str, appointment_id: int, action: str):
    """
    Helper function to send notifications to doctor and patient
    """
    evolMngr = EvolutionApiManager()
    
    # Send message to doctor
    if hasattr(doctor, 'telefono') and doctor.telefono:
        try:
            response = evolMngr.send_message(doctor.telefono, mssg_dtr)
            if not response['ok']:
                logger.error(response['error'])
            logger.info(f"Successfully sent {action} notification to doctor {doctor.id} for appointment {appointment_id}")
        except Exception as e:
            logger.error(f"Failed to send {action} notification to doctor {doctor.id} for appointment {appointment_id}: {str(e)}")
    else:
        logger.warning(f"Doctor {doctor.id} has no phone number for appointment {appointment_id}")
    
    # Send message to patient
    patient_phone = getattr(paciente, 'telf_pac', None) or getattr(paciente, 'telefono', None)
    if patient_phone:
        try:
            response = evolMngr.send_message(patient_phone, mssg_pct)
            if not response['ok']:
                logger.error(response['error'])
            logger.info(f"Successfully sent {action} notification to patient {paciente.id} for appointment {appointment_id}")
        except Exception as e:
            logger.error(f"Failed to send {action} notification to patient {paciente.id} for appointment {appointment_id}: {str(e)}")
    else:
        logger.warning(f"Patient {paciente.id} has no phone number for appointment {appointment_id}")

# Optional: Add a utility function for manual notifications
def send_appointment_reminder(cita_id: int):
    """
    Utility function to manually send appointment reminders
    """
    try:
        cita = Cita.objects.get(id=cita_id)
        
        dia_nombre = DIAS_SEMANA.get(cita.fecha.weekday(), 'N/A')
        fecha_formateada = cita.fecha.strftime('%d/%m/%Y')
        
        mssg_pct = f'''🔔 Recordatorio: Tiene una cita programada para mañana
                   {dia_nombre} {fecha_formateada} a las {cita.hora}. 
                   Doctor: {cita.medico.nombre if hasattr(cita.medico, "nombre") else "N/A"}'''
        
        mssg_dtr = f'''🔔 Recordatorio de cita:
                   Paciente: {cita.paciente.nombre if hasattr(cita.paciente, "nombre") else "N/A"}
                   Fecha: {dia_nombre} {fecha_formateada}
                   Hora: {cita.hora}'''
        
        _send_notifications(cita.medico, cita.paciente, mssg_dtr, mssg_pct, cita.id, "reminder")
        
    except Cita.DoesNotExist:
        logger.error(f"Appointment with id {cita_id} does not exist")
    except Exception as e:
        logger.error(f"Failed to send reminder for appointment {cita_id}: {str(e)}")