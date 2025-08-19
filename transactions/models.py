from django.db import models
from core.models import (
    Paciente,
    Cita,
)
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class Ingreso(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.SET_NULL, null=True, blank=False)
    monto = models.FloatField()
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True, blank=False)
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    metodo = models.CharField(max_length=50, default='Efectivo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.paciente} : {self.created_at}"
    
class Egreso(models.Model):
    monto = models.FloatField()
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(max_length=2000, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.created_at} : S/{self.monto}'