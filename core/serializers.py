# your_app/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
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
    PacientePlaca,
    )

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
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
        if not value.rol == 'medico':
            raise serializers.ValidationError("El usuario seleccionado no está marcado como médico.")
        return value

    def validate_hora(self, value):
        """Ensure time is only in 15-minute intervals."""
        if value.minute % 15 != 0 or value.second != 0 or value.microsecond != 0:
            raise serializers.ValidationError(
                "La hora debe estar en intervalos de 15 minutos (ej. 7:00, 7:15, 7:30, 7:45)."
            )
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

class EnfermedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enfermedad
        fields = '__all__'

class PacienteEvolucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacienteEvolucion
        fields = '__all__'


class PacienteDiagnosticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacienteDiagnostico
        fields = '__all__'

class PacientePlacaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PacientePlaca
        fields = '__all__'
