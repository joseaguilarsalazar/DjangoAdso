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
    # Keeping the name as 'anotaciones' so it perfectly matches your frontend table
    anotaciones = serializers.CharField(source='anotacion', read_only=True, default='Sin anotaciones')
    clinica = serializers.SerializerMethodField()
    
    class Meta:
        model = Cita
        fields = ['paciente', 'hora', 'anotaciones', 'clinica']
    
    def get_paciente(self, obj):
        return str(obj.paciente) if obj.paciente else "Paciente no registrado"

    def get_clinica(self, obj):
        # Safely navigate from Cita -> Paciente -> Clinica
        if obj.paciente and obj.paciente.clinica:
            return obj.paciente.clinica.nombre
        return "Clínica no asignada"


class AppointmentsByDoctorApiView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve appointments for the authenticated doctor on a specific date.
        Query params:
            - fecha: ISO format date (YYYY-MM-DD), defaults to today
            - medico_id: ID of the doctor
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

        # Update select_related to traverse the relationship to the clinic
        appointments = Cita.objects.filter(
            medico=doctor, 
            fecha=appointment_date_filter
        ).select_related('paciente', 'paciente__clinica').order_by('hora')

        serializer = AppointmentsByDoctorSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)