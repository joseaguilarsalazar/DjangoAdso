from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models import Paciente, Clinica  # Adjust import based on your file structure


class EncuestaStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        dni_medico = request.data.get('dni_medico')

        if not dni_medico:
            return Response(
                {"error": "El parámetro 'dni_medico' es requerido en el cuerpo de la solicitud."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Obtener la clínica destino
        target_clinica = Clinica.objects.filter(nomb_clin="Clinica Dental Sede Misti").first()
        if not target_clinica:
            return Response(
                {"error": "La clínica 'Clinica Dental Sede Misti' no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Obtener la lista de DNIs que YA existen en la clínica de destino
        # Excluimos valores nulos por si acaso hay registros incompletos
        existing_dnis = Paciente.objects.filter(
            clinica=target_clinica
        ).exclude(
            dni_pac__isnull=True
        ).values_list('dni_pac', flat=True)

        # 3. Buscar los IDs de los pacientes del médico que:
        #    - NO estén ya en la clínica objetivo.
        #    - Su DNI NO figure en la lista de DNIs existentes (¡Aquí ocurre la magia de ignorar!).
        patient_ids = list(
            Paciente.objects.filter(
                cita__medico__num_doc=dni_medico,
                cita__medico__rol='medico'
            ).exclude(
                clinica=target_clinica
            ).exclude(
                dni_pac__in=existing_dnis
            ).values_list('id', flat=True).distinct()
        )

        total_updated = len(patient_ids)

        # 4. Actualizar masivamente en una sola consulta SQL segura
        if total_updated > 0:
            Paciente.objects.filter(id__in=patient_ids).update(clinica=target_clinica)
        
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