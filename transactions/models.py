from django.db import models
from core.models import (
    Paciente,
    Cita,
)
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class Pagos(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.SET_NULL, null=True)
    monto = models.FloatField()
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True)
    metodo = models.CharField(max_length=50, default='Efectivo')
    fechaVencimiento = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.paciente.__str__} : {self.created_at}'
    