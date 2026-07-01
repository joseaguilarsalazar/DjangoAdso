from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models import Paciente, Clinica


class TransferDataView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Obtener la clínica destino
        target_clinica = Clinica.objects.filter(nomb_clin="Clinica Dental Sede Misti").first()
        if not target_clinica:
            return Response(
                {"error": "La clínica 'Clinica Dental Sede Misti' no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Obtener la lista de DNIs que YA existen en la clínica de destino
        existing_dnis = Paciente.objects.filter(
            clinica=target_clinica
        ).exclude(
            dni_pac__isnull=True
        ).values_list('dni_pac', flat=True)

        # 3. Buscar los QuerySet de los pacientes (Corregido el camino del ORM)
        # Cambiado de list() a un QuerySet directo para optimizar el rendimiento
        patients_to_update = Paciente.objects.filter(
            cita__consultorio__clinica__nomb_clin="Clinica Dental Sede Iquitos"
        ).exclude(
            clinica=target_clinica
        ).exclude(
            dni_pac__in=existing_dnis
        ).distinct()

        total_updated = patients_to_update.count()

        # 4. Actualizar masivamente en una sola consulta SQL segura
        if total_updated > 0:
            patients_to_update.update(clinica=target_clinica)
        
        return Response(
            {
                "message": "Proceso de actualización masiva finalizado.",
                "detalles": {
                    "pacientes_actualizados": total_updated,
                    "nota": "Cualquier paciente que presentara un DNI duplicado con la sede destino fue ignorado de manera automática."
                }
            },
            status=status.HTTP_200_OK
        )