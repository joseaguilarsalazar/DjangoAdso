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
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    password2 = serializers.CharField(write_only=True, required=False)
    class  Meta:
        model = User
        # excluimos campos sensibles o de sistema
        exclude = ['groups', 'user_permissions', 'old_cod_med']
        read_only_fields = ['id', 'created_at', 'updated_at']

    
    def validate(self, attrs):
        # si se envían password y password2, validarlas
        pwd = attrs.get('password')
        pwd2 = attrs.get('password2')
        if pwd or pwd2:
            if pwd != pwd2:
                raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
        else:
            # si quieres forzar password requerido al crear, lanza error aquí
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        # quita password2 si existe
        validated_data.pop('password2', None)
        password = validated_data.pop('password', None)

        # actualizar campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # si viene contraseña, usar set_password
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        # excluimos campos sensibles o de sistema
        exclude = ['old_cod_pac']
        read_only_fields = ['id', 'created_at', 'updated_at']
        

class TratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tratamiento
        fields = '__all__'

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'

class CustomPacienteSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source="nomb_pac")
    apellido = serializers.CharField(source="apel_pac")
    dni = serializers.CharField(source = 'dni_pac')
    edad = serializers.CharField(source = 'edad_pac')
    telefono = serializers.CharField(source = 'telf_pac')
    estado = serializers.CharField(source = 'esta_pac')

    class Meta:
        model = Paciente
        fields = [
            "id",
            "nombre",    
            "apellido", 
            "edad",
            "dni",
            "telefono",
            "estado",
        ]

class MedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "telefono",
            "rol",
            "estado",
        ]
class CitaSerializer(serializers.ModelSerializer):
    paciente = CustomPacienteSerializer(read_only=True)
    medico = MedicoSerializer(read_only=True)

    class Meta:
        model = Cita
        exclude = ["reminder_sent", "cancelado", "reprogramado", "old_cod_cit"]

    def validate_medico(self, value):
        if not value.rol == "medico":
            raise serializers.ValidationError("El usuario seleccionado no está marcado como médico.")
        return value

    def validate_hora(self, value):
        """Ensure time is only in 30-minute intervals."""
        if value.minute % 30 != 0 or value.second != 0 or value.microsecond != 0:
            raise serializers.ValidationError(
                "La hora debe estar en intervalos de 30 minutos (ej. 7:00, 7:30, 8:00, 8:30)."
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
