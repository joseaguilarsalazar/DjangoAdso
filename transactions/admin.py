from django.contrib import admin
from .models import (
    Pagos,
    Honorarios,
)

# Register your models here.
admin.site.register(Pagos)
admin.site.register(Honorarios)