from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models import Paciente, Clinica, TratamientoPaciente, Cita  # Adjust import based on your file structure
from django.db import transaction

class TransferDataView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        dni_medico = request.data.get('dni_medico')

        if not dni_medico:
            return Response(
                {"error": "El parámetro 'dni_medico' es requerido en el cuerpo de la solicitud."},
                status=status.HTTP_400_BAD_REQUEST
            )

        target_clinica = Clinica.objects.filter(nomb_clin="Clinica Dental Sede Misti").first()
        if not target_clinica:
            return Response(
                {"error": "La clínica 'Clinica Dental Sede Misti' no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 1. Obtener los objetos completos de los pacientes involucrados
        patients_to_process = Paciente.objects.filter(
            cita__medico__num_doc=dni_medico,
            cita__medico__rol='medico'
        ).distinct()

        # 2. Mapear los DNI de los pacientes que YA existen en la clínica de destino para detectar conflictos velozmente
        existing_dnis_in_target = set(
            Paciente.objects.filter(clinica=target_clinica).values_list('dni_pac', flat=True)
        )

        ids_to_bulk_update = []
        merged_count = 0
        updated_count = 0

        # Ejecutamos todo en una transacción atómica para que si algo falla, no quede información a medias
        with transaction.atomic():
            for patient in patients_to_process:
                # Si el paciente ya pertenece a la clínica objetivo, no hacemos nada
                if patient.clinica == target_clinica:
                    continue

                if patient.dni_pac in existing_dnis_in_target:
                    # --- LÓGICA DE FUSIÓN (EL PACIENTE YA EXISTE EN LA SEDE MISTI) ---
                    target_patient = Paciente.objects.filter(dni_pac=patient.dni_pac, clinica=target_clinica).first()
                    
                    if target_patient:
                        # a. Traspasar todo el historial de citas a la ficha destino
                        Cita.objects.filter(paciente=patient).update(paciente=target_patient)
                        
                        # b. Traspasar todos los tratamientos registrados a la ficha destino
                        TratamientoPaciente.objects.filter(paciente=patient).update(paciente=target_patient)
                        
                        # c. Consolidar información médica de texto (Observaciones y Odontograma)
                        if patient.observacion:
                            if target_patient.observacion:
                                target_patient.observacion = f"{target_patient.observacion} | Nota sede previa: {patient.observacion}"
                            else:
                                target_patient.observacion = patient.observacion

                        if patient.detalleodontograma_pac and not target_patient.detalleodontograma_pac:
                            target_patient.detalleodontograma_pac = patient.detalleodontograma_pac
                        
                        target_patient.save()
                        
                        # d. Eliminar la ficha vieja de la otra clínica para no dejar basura ni duplicados
                        patient.delete()
                        merged_count += 1
                else:
                    # --- SIN CONFLICTO ---
                    # Es seguro migrarlo directamente mudando su ID de clínica
                    ids_to_bulk_update.append(patient.id)

            # 3. Ejecutar la actualización masiva para los pacientes que no tenían historial duplicado
            if ids_to_bulk_update:
                Paciente.objects.filter(id__in=ids_to_bulk_update).update(clinica=target_clinica)
                updated_count = len(ids_to_bulk_update)
        
        return Response(
            {
                "message": f"Proceso de unificación completado con éxito.",
                "detalles": {
                    "pacientes_migrados_directamente": updated_count,
                    "pacientes_fusionados_por_duplicidad": merged_count,
                    "total_procesados": updated_count + merged_count
                }
            },
            status=status.HTTP_200_OK
        )