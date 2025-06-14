# your_app/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Historial, Tratamiento, Especialidad, Cita, Pagos, Paciente

User = get_user_model()


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

class PagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagos
        fields = '__all__'