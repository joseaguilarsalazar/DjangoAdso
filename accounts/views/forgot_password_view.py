from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from ..serializers import ForgotPasswordSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings

User = get_user_model()

class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot-password/
    {
      "email": "usuario@example.com"
    }
    Responses:
    - 200 OK:
      { "detail": "Se ha enviado el enlace de restablecimiento de contraseña al correo proporcionado." }
    - 400 Bad Request (email no existe):
      { "email": ["No encontramos un usuario con ese correo."] }
    - 400 Bad Request (formato inválido):
      { "email": ["Este campo debe ser un email válido."] }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        if not User.objects.filter(email=email).exists():
            return Response(
                {"email": ["No encontramos un usuario con ese correo."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Envía el email usando el form de Django
        form = PasswordResetForm(data={"email": email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                email_template_name='../templates/auth/password_reset_email.html',
            )
            return Response(
                {"detail": "Se ha enviado el enlace de restablecimiento de contraseña al correo proporcionado."},
                status=status.HTTP_200_OK
            )

        # En la práctica form.is_valid() siempre será True si el email existe,
        # pero por completitud devolvemos este fallback:
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)