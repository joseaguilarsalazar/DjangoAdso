from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Count, Min, OuterRef, Subquery
from core.models import Paciente, Cita

class PatientsByDoctorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 1. Subquery para obtener el ID del primer médico histórico de cada paciente
            first_appointment = Cita.objects.filter(
                paciente_id=OuterRef('id'),
                medico__isnull=False
            ).order_by('fecha', 'hora').values('medico_id')[:1]

            # 2. Obtener un resumen de citas por paciente y médico
            # Esto nos dará una fila por cada combinación de Paciente-Médico con su conteo
            appointments_summary = (
                Cita.objects.filter(medico__isnull=False, paciente__isnull=False)
                .values('paciente_id', 'medico_id', 'medico__name')
                .annotate(citas_con_medico=Count('id'))
                .order_by('paciente_id', '-citas_con_medico')
            )

            # 3. Mapear todos los pacientes a sus datos básicos y su primer médico
            # Traemos solo los campos necesarios para optimizar la memoria
            patients_base = {
                p['id']: {
                    'full_name': f"{p['nomb_pac']} {p['apel_pac']}".strip(),
                    'phone': p['telf_pac'] or "---",
                    'first_doctor_id': p['first_doc'],
                    'total_citas': 0,
                    'medicos_conteo': {} # {medico_id: {count, name}}
                }
                for p in Paciente.objects.annotate(
                    first_doc=Subquery(first_appointment)
                ).values('id', 'nomb_pac', 'apel_pac', 'telf_pac', 'first_doc')
            }

            # 4. Consolidar los conteos de citas en nuestro diccionario de pacientes
            # Determinamos cuántas citas tiene el paciente con cada médico y su total general
            for entry in appointments_summary:
                p_id = entry['paciente_id']
                m_id = entry['medico_id']
                count = entry['citas_con_medico']
                m_name = f"{entry['medico__name']} {entry.get('medico__last_name', '')}".strip() or f"Médico {m_id}"

                if p_id in patients_base:
                    patients_base[p_id]['total_citas'] += count
                    patients_base[p_id]['medicos_conteo'][m_id] = {
                        'count': count,
                        'name': m_name
                    }

            # Estructura final de respuesta por doctor
            # Usamos "Sin Asignar" para los pacientes que no registran citas con médicos válidos
            doctors_group = {
                "Sin Asignar": []
            }

            # Helper para registrar pacientes dentro del grupo de un doctor en el diccionario
            def add_to_doctor(doc_name, patient_info):
                if doc_name not in doctors_group:
                    doctors_group[doc_name] = []
                doctors_group[doc_name].append({
                    "nombre_completo": patient_info['full_name'],
                    "telefono": patient_info['phone']
                })

            # 5. Aplicar las Reglas de Negocio para la asignación
            for p_id, p_info in patients_base.items():
                total = p_info['total_citas']
                medicos = p_info['medicos_conteo']

                if total == 0 or not medicos:
                    add_to_doctor("Sin Asignar", p_info)
                    continue

                # Encontrar el médico con más citas para este paciente
                top_doctor_id = max(medicos, key=lambda k: medicos[k]['count'])
                top_doctor_count = medicos[top_doctor_id]['count']
                top_doctor_name = medicos[top_doctor_id]['name']

                # --- REGLA 1: 90% o más de las citas con un solo doctor ---
                if (top_doctor_count / total) >= 0.90:
                    add_to_doctor(top_doctor_name, p_info)
                    continue

                # --- REGLA 2: Menos de 3 citas en total -> Asignar al primero ---
                if total < 3:
                    first_doc_id = p_info['first_doctor_id']
                    if first_doc_id in medicos:
                        add_to_doctor(medicos[first_doc_id]['name'], p_info)
                    else:
                        # Fallback seguro al de mayor cantidad si el primero por alguna razón es nulo
                        add_to_doctor(top_doctor_name, p_info)
                    continue

                # --- REGLA 3: Más de 3 citas (o igual a 3) -> Asignar al de más citas ---
                if total >= 3:
                    add_to_doctor(top_doctor_name, p_info)

            return Response(doctors_group, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            return Response({
                "error": "Error interno del servidor",
                "details": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)