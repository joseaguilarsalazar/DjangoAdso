from django.contrib import admin
from .models import (
    Tratamiento, 
    Especialidad, 
    Cita, 
    Paciente,
    Clinica,
    Alergia,
    PacienteAlergia,
    Banco,
    Categoria,
    Enfermedad,
    PacienteEvolucion,
    PacienteEnfermedad,
    PacienteDiagnostico,
    PacientePlaca, Consultorio, CategoriaTratamiento,
    TratamientoPaciente,
    )

# Register your models here.
admin.site.register(Especialidad)
admin.site.register(Paciente)
admin.site.register(Cita)
admin.site.register(Tratamiento)
admin.site.register(Clinica)
admin.site.register(Alergia)
admin.site.register(PacienteAlergia)
admin.site.register(Banco)
admin.site.register(Categoria)
admin.site.register(Enfermedad)
admin.site.register(PacienteEvolucion)
admin.site.register(PacienteEnfermedad)
admin.site.register(PacienteDiagnostico)
admin.site.register(PacientePlaca)
admin.site.register(Consultorio)
admin.site.register(CategoriaTratamiento)
admin.site.register(TratamientoPaciente)