# your_app/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Historial, Tratamiento, Especialidad, Medico, Cita, Pagos

User = get_user_model()


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # excluimos campos sensibles o de sistema
        fields = [
            'id',
            'tipo_doc',
            'num_doc',
            'name',
            'email',
            'rol',
            'estado',
            'foto',
            'telefono',
            'id_medico',
            'created_at',
            'updated_at',
        ]
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

class MedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medico
        fields = '__all__'

class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = '__all__'

class PagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagos
        fields = '__all__'