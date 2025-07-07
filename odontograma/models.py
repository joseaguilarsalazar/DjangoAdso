from django.db import models
from core.models import Paciente
import os


# Create your models here.
class Odontograma(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    especificaciones = models.TextField(max_length=2000, null=True, blank=True)
    observaciones = models.TextField(max_length=2000, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Diente(models.Model):
    numeroDiente = models.IntegerField()
    iconoPorDefecto = models.ImageField(upload_to='odontograma/iconos_default/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Diente {self.numeroDiente}'

def odontograma_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.odontograma.paciente.id}_{instance.diente.numeroDiente}.{ext}"
    return os.path.join('odontograma/pacientes/', filename)

class DienteOdontograma(models.Model):
    diente = models.ForeignKey(Diente, on_delete=models.SET_NULL, null=True)
    odontograma = models.ForeignKey(Odontograma, on_delete=models.CASCADE)
    iconoModificado = models.ImageField(upload_to=odontograma_upload_path, null=True, blank=True)
    datosRecuadro = models.CharField(max_length=3, default="", blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CasoMultidental(models.Model):
    odontograma = models.ForeignKey(Odontograma, on_delete=models.CASCADE)
    dienteExtremo1 = models.ForeignKey(Diente, on_delete=models.SET_NULL, null=True, related_name='diente_extremo_1')
    dienteExtremo2 = models.ForeignKey(Diente, on_delete=models.SET_NULL, null=True, related_name='diente_extremo_2')

    TIPOS_CASO_DICT = {
    'TRAN': 'Transposición',
    'SUP': 'Supernumerario',
    'PTOT': 'Prótesis Total',
    'PREM': 'Prótesis Removible',
    'GFUS': 'Geminación / Fusión',
    'EDTO': 'Edéntulo Total',
    'DIA':  'Diastema',
    'AOR':  'Aparato Ortodóntico Removible',
    'AOF':  'Aparato Ortodóntico Fijo'
    }

    TIPOS = [(k, v) for k, v in TIPOS_CASO_DICT.items()]

    caso = models.CharField(choices=TIPOS, default=None, null=True, blank=True, max_length=5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)