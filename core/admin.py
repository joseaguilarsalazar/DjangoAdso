from django.contrib import admin
from .models import (Especialidad, Medico, Cita, Paciente, Historial, Pagos, Tratamiento)

# Register your models here.
admin.site.register(Especialidad)
admin.site.register(Medico)
admin.site.register(Paciente)
admin.site.register(Historial)
admin.site.register(Cita)
admin.site.register(Pagos)
admin.site.register(Tratamiento)