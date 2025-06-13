from rest_framework import generics
from ..serializers import RegisterSerializer
from rest_framework.permissions import AllowAny

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    
    Request:
    {
      "name": "Juan Pérez",
      "email": "juan@example.com",
      "password": "secret123",
      "password_confirmation": "secret123",
      "tipo_doc": "CC",
      "num_doc": "1234567890",
      "rol": "paciente",
      "estado": "activo",
      "telefono": "3001234567",
      "id_medico": null
    }

    Response 201 Created:
    {
      "id": 10,
      "email": "juan@example.com",
      "name": "Juan Pérez",
      "tipo_doc": "CC",
      "num_doc": "1234567890",
      "rol": "paciente",
      "estado": "activo",
      "telefono": "3001234567",
      "foto": null,
      "id_medico": null
    }
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
