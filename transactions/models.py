from django.db import models
from django.db import transaction
from core.models import (
    TratamientoPaciente, Clinica
)
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class Ingreso(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tratamientoPaciente = models.ForeignKey(
        TratamientoPaciente, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=False,
        related_name='ingresos' 
        )
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    porcentaje_medico = models.FloatField(null=True, blank=True) #from 0 to 100

    METODO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta', 'Tarjeta'),
        ('Transferencia', 'Transferencia'),
    ]
    metodo = models.CharField(max_length=50, choices=METODO_CHOICES, default='Efectivo')
    fecha_registro = models.DateField(null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Egreso(models.Model):
    monto = models.FloatField()
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(max_length=2000, null=True, blank=True)
    tratamientoPaciente = models.ForeignKey(
        TratamientoPaciente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, null=True, blank=True)

    TYPE_CHOICES = [
        ('LAB', 'Laboratorio'),
        ('DOC', 'Pago Medico'),
        ('CLI', 'Clinica'),
    ]
    tipo = models.CharField(max_length=3, choices=TYPE_CHOICES, default='CLI')

    source_ingreso = models.ForeignKey(
        Ingreso, 
        on_delete=models.CASCADE, # If income is deleted, commission is deleted
        null=True, 
        blank=True,
        related_name='generated_egresos'
    )

    fecha_registro = models.DateField(null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.created_at} : S/{self.monto}'
    
    def tipoEgreso(self):
        if self.tratamientoPaciente and self.medico:
            return "odontologo"
        elif self.tratamientoPaciente:
            return "lab"
        else:
            return "clinica"
        



# 1000, 200
# 800 400
#dfio23uy4r9p8023u45r2l3krfj