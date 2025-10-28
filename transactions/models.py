from django.db import models
from django.db import transaction
from core.models import (
    TratamientoPaciente, Clinica
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
    fecha_registro = models.DateField(null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        # Save the Ingreso first
        with transaction.atomic():
            super().save(*args, **kwargs)
            if is_new and self.tratamientoPaciente:
                # Calculate net amount after lab expenses for this tratamiento
                total_lab_egresos = Egreso.objects.filter(
                    tratamientoPaciente=self.tratamientoPaciente,
                    medico__isnull=True
                ).aggregate(models.Sum('monto'))['monto__sum'] or 0.0
                
                net_amount = float(self.monto) - total_lab_egresos
                
                if net_amount > 0:
                    percentage = 0.5 if self.medico.is_especialista else 0.4
                    egreso_monto = net_amount * percentage
                    Egreso.objects.create(
                        monto=egreso_monto,
                        medico=self.medico,
                        tratamientoPaciente=self.tratamientoPaciente,
                        description='pago al medico',
                        fecha_registro=self.fecha_registro
                    )

    def __str__(self):
        # previously referenced self.paciente which doesn't exist; show tratamientoPaciente instead
        return f"{self.tratamientoPaciente.tratamiento.nombre}"
    
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
        
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            if is_new and self.tipoEgreso() == 'lab' and self.tratamientoPaciente:
                # Recalculate doctor egresos for this tratamientoPaciente after lab expense
                # 1. Get all ingresos ordered by creation date (oldest first)
                ingresos = Ingreso.objects.filter(
                    tratamientoPaciente=self.tratamientoPaciente
                ).order_by('created_at')
                
                # 2. Calculate total lab egresos (including this new one)
                total_lab_egresos = Egreso.objects.filter(
                    tratamientoPaciente=self.tratamientoPaciente,
                    medico__isnull=True
                ).aggregate(models.Sum('monto'))['monto__sum'] or 0.0
                
                # 3. Consume lab expenses sequentially from ingresos
                remaining_lab_expense = total_lab_egresos
                
                for ingreso in ingresos:
                    if ingreso.medico:
                        ingreso_monto = float(ingreso.monto)
                        
                        # Calculate net amount after deducting remaining lab expense
                        if remaining_lab_expense > 0:
                            # This ingreso must cover (part of) the lab expense first
                            net_amount = max(0, ingreso_monto - remaining_lab_expense)
                            remaining_lab_expense = max(0, remaining_lab_expense - ingreso_monto)
                        else:
                            # Lab expenses fully covered, full amount goes to doctor calculation
                            net_amount = ingreso_monto
                        
                        # Find existing doctor egreso for this tratamiento and doctor
                        doctor_egreso = Egreso.objects.filter(
                            tratamientoPaciente=self.tratamientoPaciente,
                            medico=ingreso.medico,
                            description='pago al medico'
                        ).first()
                        
                        if net_amount > 0:
                            percentage = 0.5 if ingreso.medico.is_especialista else 0.4
                            new_egreso_monto = net_amount * percentage
                            
                            if doctor_egreso:
                                # Update existing egreso
                                doctor_egreso.monto = new_egreso_monto
                                doctor_egreso.save(update_fields=['monto', 'updated_at'])
                            else:
                                # Create new egreso if it doesn't exist
                                Egreso.objects.create(
                                    monto=new_egreso_monto,
                                    medico=ingreso.medico,
                                    tratamientoPaciente=self.tratamientoPaciente,
                                    description='pago al medico',
                                    fecha_registro=ingreso.fecha_registro
                                )
                        else:
                            # Net amount is 0 or negative, delete existing egreso if it exists
                            if doctor_egreso:
                                doctor_egreso.delete()



# 1000, 200
# 800 400
#dfio23uy4r9p8023u45r2l3krfj