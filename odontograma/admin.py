from django.contrib import admin
from .models import (
    Diente,
    Odontograma,
    CasoMultidental,
)
# Register your models here.
admin.site.register(Diente)
admin.site.register(Odontograma)
admin.site.register(CasoMultidental)