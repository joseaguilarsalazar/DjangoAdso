# your_app/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Historial, 
    Tratamiento, 
    Especialidad, 
    Cita, 
    Paciente,
    Clinica,
    Alergia,
    PacienteAlergia,
    Banco,
    Categoria,
    PacienteTratamiento,
    Enfermedad,
    PacienteEvolucion,
    PacienteEnfermedad,
    )

User = get_user_model()

class UserSerialier(serializers.ModelSerializer):
    class  Meta:
        model = User
        # excluimos campos sensibles o de sistema
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        # excluimos campos sensibles o de sistema
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class HistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historial
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class TratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tratamiento
        fields = '__all__'

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'

class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = '__all__'

    def validate_medico(self, value):
        if not value.medico:
            raise serializers.ValidationError("El usuario seleccionado no está marcado como médico.")
        return value
    
class ClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinica
        fields = '__all__'

class AlergiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alergia
        fields = '__all__'

class PacienteAlergiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacienteAlergia
        fields = '__all__'

class PacienteEnfermedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacienteEnfermedad
        fields = '__all__'

class BancoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banco
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class PacienteTratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacienteTratamiento
        fields = '__all__'

class EnfermedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enfermedad
        fields = '__all__'

class PacienteEvolucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacienteEvolucion
        fields = '__all__'