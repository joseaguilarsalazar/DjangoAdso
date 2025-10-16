from django.db import models
from django.db import transaction
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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        # Save the Ingreso first
        with transaction.atomic():
            super().save(*args, **kwargs)
            if is_new:
                # create corresponding Egreso for 40% payment to the medico
                percentage = 0.5 if self.medico.is_especialista else 0.4
                egreso_monto = float(self.monto) * percentage if self.monto is not None else 0.0
                Egreso.objects.create(
                    monto=egreso_monto,
                    medico=self.medico,
                    description='pago al medico'
                )

    def __str__(self):
        # previously referenced self.paciente which doesn't exist; show tratamientoPaciente instead
        return f"{self.tratamientoPaciente} : {self.created_at}"
    
class Egreso(models.Model):
    monto = models.FloatField()
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(max_length=2000, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.created_at} : S/{self.monto}'