from django.db import models
from core.models import Paciente

# Create your models here.

class Chat(models.Model):
    STATE_CHOICES = [
        ("default", "Default"),
        ("appointment_lookup", "Appointment Lookup"),
        ("patient_registration", "Patient Registration"),
    ]
    number = models.CharField(unique=True, max_length=20)
    current_state = models.CharField(max_length=100, choices=STATE_CHOICES, default="default")
    patient = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True, blank=True)

    def last_messages(self, limit=20):
        return Message.objects.filter(chat_id=self.id).order_by("created_at").reverse()[:limit]

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    text = models.CharField(max_length=2000)
    from_user = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)