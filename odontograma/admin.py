from django.contrib import admin
from .models import (
    Diente,
    DienteOdontograma,
    Odontograma,
    CasoMultidental,
)
# Register your models here.
admin.site.register(Diente)
admin.site.register(DienteOdontograma)
admin.site.register(Odontograma)
admin.site.register(CasoMultidental)