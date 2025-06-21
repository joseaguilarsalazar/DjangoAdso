from django.db import models
from core.models import Paciente


# Create your models here.
class Odontograma(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)