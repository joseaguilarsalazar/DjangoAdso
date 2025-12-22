from django.db import models
from core.models import Paciente

class Odontograma(models.Model):
    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.CASCADE,
        related_name='odontogramas' # Allows accessing via paciente.odontogramas.all()
    )
    
    drawings = models.JSONField(
        default=dict, 
        blank=True, 
        help_text="Normalized vector paths grouped by Tooth ID"
    )

    preview_image = models.ImageField(upload_to='odontogramas/previews/', null=True, blank=True)

    especificaciones = models.TextField(max_length=2000, blank=True)
    observaciones = models.TextField(max_length=2000, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at'] # Shows newest charts first by default

    def __str__(self):
        return f"Odontograma {self.paciente} - {self.created_at.date()}"
    
    @property
    def teeth_treated_count(self):
        """Helper to count how many teeth have drawings"""
        if self.drawings:
            return len(self.drawings.keys())
        return 0


class Diente(models.Model):
    """
    STATIC TABLE (Populate once).
    Serves as the 'Map Configuration'.
    """
    numero = models.IntegerField(unique=True)
    
    hitbox_json = models.JSONField(help_text="Coordinates for zoom/click detection on the master map")

    def __str__(self):
        return f"Diente {self.numero}"


class Hallazgo(models.Model):
    odontograma = models.ForeignKey(Odontograma, related_name='hallazgos', on_delete=models.CASCADE)
    diente = models.ForeignKey(Diente, on_delete=models.PROTECT)
    
    condicion = models.CharField(max_length=50) 
    
    superficie = models.CharField(max_length=50, blank=True, null=True) 
    estado = models.CharField(max_length=10, blank=True, null=True, choices=[('GOOD', 'Bueno/Azul'), ('BAD', 'Malo/Rojo')])

    class Meta:
        unique_together = ('odontograma', 'diente')
    

class CasoMultidental(models.Model):
    """
    Perfect approach for bridges/brackets that span multiple teeth.
    """
    odontograma = models.ForeignKey(Odontograma, on_delete=models.CASCADE, related_name='casos_multidentales')
    dienteStart = models.ForeignKey(Diente, on_delete=models.PROTECT, related_name='caso_start')
    dienteEnd = models.ForeignKey(Diente, on_delete=models.PROTECT, related_name='caso_end')

    class TipoCaso(models.TextChoices):
        TRANSPOSICION = 'TRAN', 'Transposición'
        SUPERNUMERARIO = 'SUP', 'Supernumerario'
        PROTESIS_TOTAL = 'PTOT', 'Prótesis Total'
        PROTESIS_REMOVIBLE = 'PREM', 'Prótesis Removible'
        GEMINACION = 'GFUS', 'Geminación / Fusión'
        EDENTULO = 'EDTO', 'Edéntulo Total'
        DIASTEMA = 'DIA', 'Diastema'
        ORTODONCIA_REM = 'AOR', 'Aparato Ortodóntico Removible'
        ORTODONCIA_FIJ = 'AOF', 'Aparato Ortodóntico Fijo'
        PUENTE = 'PUE', 'Puente Fijo' # Common in Peru

    caso = models.CharField(choices=TipoCaso.choices, max_length=5)
    
    # Store drawing data for the bridge/connector line itself
    drawing_json = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)