from django.contrib import admin
from .models import (
    Ingreso,
    Egreso
)

# Register your models here.
admin.site.register(Ingreso)
admin.site.register(Egreso)