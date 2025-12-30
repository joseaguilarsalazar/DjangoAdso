from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from ..serializers import ResetPasswordSerializer
from rest_framework.response import Response
from rest_framework import status

class ResetPasswordView(APIView):
    """
    POST /api/auth/reset-password/
    {
      "email": "usuario@example.com",
      "token": "<el-token-recibido-por-email>",
      "password": "nuevaClave123",
      "password_confirmation": "nuevaClave123"
    }

    Respuestas:
    - 200 OK:
      { "detail": "Contraseña restablecida con éxito." }
    - 400 Bad Request (email inválido, token inválido o contraseñas no coinciden):
      {
        "email": ["No existe un usuario con este correo."],
        "token": ["Token inválido o expirado."],
        "password_confirmation": ["Las contraseñas no coinciden."]
      }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(
            {"detail": "Contraseña restablecida con éxito."},
            status=status.HTTP_200_OK
        )