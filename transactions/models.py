from django.db import models
from core.models import (
    Paciente,
    PacienteTratamiento
)
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class Pagos(models.Model):
    pacienteTratamiento = models.ForeignKey(PacienteTratamiento, on_delete=models.SET_NULL, null=True)
    monto = models.FloatField()
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True)
    fechaVencimiento = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.paciente.__str__} : {self.created_at}'
    
class Honorarios(models.Model):
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    