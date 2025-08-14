from rest_framework import views
from ..models import (
    Paciente, 
    PacienteDiagnostico, 
    PacienteAlergia, 
    PacienteEvolucion, 
    PacientePlaca,
    Cita,
    Tratamiento
    )
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from core.serializers import (
    PacienteSerializer, 
    PacienteDiagnosticoSerializer,
    PacienteAlergiaSerializer, 
    PacienteEvolucionSerializer, 
    PacientePlacaSerializer,
    CitaSerializer,
    TratamientoSerializer,
    )
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class HistorialApiView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Obtener información histórica del paciente",
        operation_description="Devuelve datos del paciente, incluyendo diagnósticos, alergias, placas, evoluciones y citas.",
        manual_parameters=[
            openapi.Parameter(
                'paciente',
                openapi.IN_QUERY,
                description="ID del paciente para obtener la información",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Datos históricos del paciente.",
                # You can replace this schema with a custom serializer if you make one
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'paciente': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'diagnosticos': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                        'alergias': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                        'placas': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                        'evoluciones': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                        'citas': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    }
                )
            ),
            404: openapi.Response(description="Paciente no existe."),
            401: openapi.Response(description="No autenticado.")
        }
    )
    def get(self, request):
        paciente_id = request.GET.get('paciente')
        paciente = Paciente.objects.filter(id=paciente_id).first()

        if not paciente:
            return Response({'error' : 'Paciente no Existe'}, status=status.HTTP_404_NOT_FOUND)

        historic_data = {}

        historic_data['paciente'] = PacienteSerializer(paciente).data

        diagnostico = PacienteDiagnostico.objects.filter(paciente__id=paciente.id)
        historic_data['diagnosticos'] = PacienteDiagnosticoSerializer(diagnostico, many=True).data if diagnostico.exists() else None
        
        alergias = PacienteAlergia.objects.filter(paciente__id=paciente.id)
        historic_data['alergias'] = PacienteAlergiaSerializer(alergias, many=True).data if alergias.exists() else None

        placas = PacientePlaca.objects.filter(paciente__id = paciente.id)
        historic_data['placas'] = PacientePlacaSerializer(placas, many=True).data if placas.exists() else None
        
        evoluciones = PacienteEvolucion.objects.filter(paciente__id = paciente.id)
        historic_data['evoluciones'] = PacienteEvolucionSerializer(evoluciones, many=True).data if evoluciones.exists() else None

        tratmientos = Tratamiento.objects.filter(paciente__id = paciente.id)
        historic_data['tratamientos'] = TratamientoSerializer(tratmientos, many=True).data if tratmientos.exists() else None


        citas = Cita.objects.filter(paciente__id = paciente.id)
        historic_data['citas'] = CitaSerializer(citas, many=True).data if citas.exists() else None

        return Response(historic_data, status=status.HTTP_200_OK) 