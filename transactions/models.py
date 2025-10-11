from django.db import models
from core.models import (
    TratamientoPaciente,
)
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class Ingreso(models.Model):
    monto = models.FloatField()
    tratamientoPaciente = models.ForeignKey(
        TratamientoPaciente, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=False,
        related_name='ingresos' 
        )
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)

    METODO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia'),
    ]
    metodo = models.CharField(max_length=50, choices=METODO_CHOICES, default='Efectivo')
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