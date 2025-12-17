from django.db import models
from core.models import Paciente

class Odontograma(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    
    # --- VISUAL LAYER ---
    # Instead of images, we store the "Digital Paper" state here.
    # This contains all the paths, lines, and colors drawn on the full map.
    # Frontend library (Fabric.js/Konva) dumps the entire canvas to this JSON.
    diagrama_json = models.JSONField(null=True, blank=True, help_text="Full canvas drawing data")
    
    # Capture the final look as one single image for quick previews/PDFs
    # (Optional, but recommended for performance)
    preview_image = models.ImageField(upload_to='odontogramas/previews/', null=True, blank=True)

    especificaciones = models.TextField(max_length=2000, blank=True)
    observaciones = models.TextField(max_length=2000, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Odontograma {self.paciente} - {self.created_at.date()}"


class Diente(models.Model):
    """
    STATIC TABLE (Populate once).
    Serves as the 'Map Configuration'.
    """
    numero = models.IntegerField(unique=True)  # 11, 12... 85
    
    # --- ZOOM LOGIC ---
    # These coordinates tell the UI where to 'camera zoom' on the base image
    # when this tooth is selected. 
    # Example: {'x': 100, 'y': 200, 'width': 50, 'height': 80}
    hitbox_json = models.JSONField(help_text="Coordinates for zoom/click detection on the master map")

    def __str__(self):
        return f"Diente {self.numero}"


class Hallazgo(models.Model):
    """
    DATA LAYER (The Logical/Legal part).
    Even if the doctor 'draws' the caries, they usually select a condition 
    to populate the legal text report automatically.
    """
    odontograma = models.ForeignKey(Odontograma, related_name='hallazgos', on_delete=models.CASCADE)
    diente = models.ForeignKey(Diente, on_delete=models.PROTECT)
    
    # e.g., 'Caries', 'Restauración', 'Ausente'
    condicion = models.CharField(max_length=50) 
    
    # Specifics like 'Mesial', 'Distal', 'Oclusal'
    superficie = models.CharField(max_length=50, blank=True, null=True) 

    # Colors required by COP (Colegio de Odontólogos del Perú)
    # This helps if you need to reconstruct statistics (e.g. "Count Red vs Blue")
    estado = models.CharField(max_length=10, choices=[('GOOD', 'Bueno/Azul'), ('BAD', 'Malo/Rojo')])

    class Meta:
        # Ensures we don't have duplicate 'Caries' entries for the same tooth in one chart
        # But allows multiple findings like (Caries + Fracture) on the same tooth? 
        # If yes, remove this unique_together. If strict, keep it.
        unique_together = ('odontograma', 'diente', 'condicion')
    

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