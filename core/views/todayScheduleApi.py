from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from ..serializers import CitaSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import Consultorio, Cita
from datetime import date
from collections import defaultdict

User = get_user_model()


class TodayScheduleApi(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Obtener agenda de hoy",
        operation_description="""
Devuelve la agenda de **todas las citas del día actual** organizadas por consultorio.

⚠️ Importante:  
Los consultorios siempre se devuelven como `"1", "2", "3", ...` para facilitar el uso en el frontend, 
independientemente de los IDs reales en la base de datos.

Cada clave corresponde a un consultorio y contiene una lista de citas.
        """,
        responses={
            200: openapi.Response(
                description="Agenda de hoy agrupada por consultorio",
                examples={
                    "application/json": {
                        "1": [
                            {
                                "id": 12,
                                "fecha": "2025-08-25",
                                "hora": "08:00:00",
                                "medico": {
                                    "id": 5,
                                    "nombre": "Dr. Juan Pérez",
                                    "estado": "Activo",
                                    "email": "juan@example.com"
                                },
                                "paciente": {
                                    "id": 3,
                                    "nombre": "Ana López",
                                    "estado": "Activo",
                                    "edad": 32,
                                    "dni": "12345678",
                                    "telefono": "987654321"
                                },
                                "consultorio": 1,
                                "created_at": "2025-08-25T10:30:00Z",
                                "updated_at": "2025-08-25T10:30:00Z"
                            }
                        ],
                        "2": [],
                        "3": []
                    }
                }
            )
        },
    )
    def get(self, request):
        user = request.user

        consultorios = Consultorio.objects.filter(clinica=user.clinica).order_by("id")
        consultorio_map = {c.id: str(i + 1) for i, c in enumerate(consultorios)}

        citas = Cita.objects.filter(
            paciente__clinica=user.clinica,
            fecha=date.today()
        ).select_related("consultorio")

        data = defaultdict(list)

        for cita in citas:
            key = consultorio_map.get(cita.consultorio_id)
            if key:
                data[key].append(CitaSerializer(cita, context={'request': self.request}).data)

        return Response(data, status=status.HTTP_200_OK)