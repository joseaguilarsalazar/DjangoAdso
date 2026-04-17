from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from datetime import date
from rest_framework import views
from ..models import Cita
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
class AppointmentsByDoctorSerializer(serializers.ModelSerializer):
    paciente = serializers.SerializerMethodField()
    hora = serializers.TimeField()
    motivo = serializers.CharField(source='anotacion')
    clinica = serializers.CharField(source='clinica.nombre')
    
    class Meta:
        model = Cita
        fields = ['paciente', 'hora', 'motivo', 'clinica']
    
    def get_paciente(self, obj):
        return str(obj.paciente)


class AppointmentsByDoctorApiView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve appointments for the authenticated doctor on a specific date.
        Query params:
            - fecha: ISO format date (YYYY-MM-DD), defaults to today
        """
        doctor_id = request.query_params.get('medico_id')
        if not doctor_id:
            return Response(
                {"error": "El parámetro 'medico_id' es requerido."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        doctor = User.objects.filter(id=doctor_id, rol='medico').first()
        if not doctor:
            return Response(
                {"error": "Odontologo no encontrado."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        appointment_date_filter = request.query_params.get('fecha')

        if appointment_date_filter:
            try:
                appointment_date_filter = date.fromisoformat(appointment_date_filter)
            except ValueError:
                return Response(
                    {"error": "Fecha inválida. Use el formato YYYY-MM-DD."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            appointment_date_filter = date.today()

        # Optimize with select_related to avoid N+1 queries
        appointments = Cita.objects.filter(
            medico=doctor, 
            fecha=appointment_date_filter
        ).select_related('paciente', 'clinica').order_by('hora')

        serializer = AppointmentsByDoctorSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)