from django.db import models
from core.models import Paciente

# Create your models here.

class Chat(models.Model):
    number = models.CharField(unique=True, max_length=20)
    current_state = models.CharField(max_length=100, default="default")
    current_sub_state = models.CharField(max_length=100, default="default")
    patient = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True, blank=True)
    data_confirmed = models.BooleanField(default=False)

    extra_data = models.JSONField(null=True, blank=True)

    def last_messages(self, limit=20):
        return Message.objects.filter(chat_id=self.id).order_by("created_at").reverse()[:limit]

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    text = models.CharField(max_length=2000)
    from_user = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

class EncuestaSatisfaccion(models.Model):
    SENTIMENT_CHOICES = [
        ('POSITIVE', 'Positivo'),
        ('NEUTRAL', 'Neutral'),
        ('NEGATIVE', 'Negativo'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='encuestas')
    fecha = models.DateTimeField(auto_now_add=True)
    texto_original = models.TextField()
    
    # AI Extracted Data
    sentimiento = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='NEUTRAL')
    aspectos_positivos = models.TextField(blank=True, help_text="JSON list of what they liked")
    areas_mejora = models.TextField(blank=True, help_text="JSON list of complaints/improvements")
    sugerencias = models.TextField(blank=True)
    
    # Value Driver: Alert Flag
    requiere_atencion_humana = models.BooleanField(default=False, help_text="True if sentiment is negative or asks for help")

    def __str__(self):
        return f"{self.paciente} - {self.sentimiento} ({self.fecha.date()})"