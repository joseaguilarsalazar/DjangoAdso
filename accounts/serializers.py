from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'password_confirmation',
            'name', 'tipo_doc', 'num_doc', 'rol', 'estado',
            'telefono', 'foto', 'direccion', 'especialidad'
        ]
        read_only_fields = ['id']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate_num_doc(self, value):
        if User.objects.filter(num_doc=value).exists():
            raise serializers.ValidationError("Este número de documento ya está registrado.")
        return value

    def validate(self, data):
        if data['password'] != data.pop('password_confirmation'):
            raise serializers.ValidationError({"password_confirmation": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            tipo_doc=validated_data['tipo_doc'],
            num_doc=validated_data['num_doc'],
            rol=validated_data['rol'],
            estado=validated_data['estado'],
            telefono=validated_data.get('telefono'),
            foto=validated_data.get('foto'),
            direccion=validated_data['direccion'],
            especialidad=validated_data.get('especialidad')
        )
        return user


    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No existe un usuario con este correo.")
        return value

    def validate(self, data):
        # Verificar que las contraseñas coincidan
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({
                "password_confirmation": "Las contraseñas no coinciden."
            })

        # Verificar el token
        user = getattr(self, 'user', None)
        token = data.get('token')
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Token inválido o expirado."})

        return data

    def save(self):
        # Aquí ya sabemos que el token es válido y las contraseñas coinciden
        password = self.validated_data['password']
        user = self.user
        user.set_password(password)
        user.save(update_fields=['password'])
        return user