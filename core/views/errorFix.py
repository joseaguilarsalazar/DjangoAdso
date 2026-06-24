from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models import Paciente, Clinica

class RevertirPacientesClinicaDosView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Recibimos los nombres de las clínicas involucradas desde el payload
        nomb_clinica_2 = "Clinica Dental Filial Yurimaguas"
        nomb_clinica_3 = "Clinica Dental Sede Misti"

        # 1. Buscar ambas instancias de clínicas en la BD
        clinica_2 = Clinica.objects.filter(nomb_clin=nomb_clinica_2).first()
        clinica_3 = Clinica.objects.filter(nomb_clin=nomb_clinica_3).first()

        if not clinica_2 or not clinica_3:
            return Response(
                {"error": "Una o ambas clínicas especificadas no existen."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Control de integridad preventivo (Anti-duplicados)
        # Obtenemos los DNIs que existen actualmente en la Clínica 2.
        # Esto evita un IntegrityError si se registró un nuevo paciente con el mismo DNI mientras duró el error.
        dnis_actuales_en_clinica_2 = Paciente.objects.filter(
            clinica=clinica_2
        ).exclude(
            dni_pac__isnull=True
        ).values_list('dni_pac', flat=True)

        # 3. Filtrar los IDs de pacientes que:
        #    - Están actualmente asignados a la Clínica 3.
        #    - Tienen al menos una Cita agendada en un Consultorio de la Clínica 2.
        #    - Su DNI no genere conflicto con registros nuevos de la Clínica 2.
        patient_ids_to_revert = list(
            Paciente.objects.filter(
                clinica=clinica_3,
                cita__consultorio__clinica=clinica_2  # Relación: Paciente -> Cita -> Consultorio -> Clinica
            ).exclude(
                dni_pac__in=dnis_actuales_en_clinica_2
            ).values_list('id', flat=True).distinct()
        )

        total_reverted = len(patient_ids_to_revert)

        # 4. Devolver masivamente a los pacientes identificados a la Clínica 2
        if total_reverted > 0:
            Paciente.objects.filter(id__in=patient_ids_to_revert).update(clinica=clinica_2)

        return Response(
            {
                "message": "Proceso de corrección y reversión finalizado.",
                "detalles": {
                    "pacientes_devueltos_a_clinica_2": total_reverted,
                    "nota": "Cualquier paciente cuyo DNI entrara en conflicto con la sede de origen fue omitido de manera segura."
                }
            },
            status=status.HTTP_200_OK
        )