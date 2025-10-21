from rest_framework import filters, viewsets
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import (
    Ingreso, Egreso
)
from .serializers import (
    IngresoSerializer,
    EgresoSerializer,
)
# Add drf_yasg imports for schema docs
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from datetime import datetime
from core.models import Paciente, TratamientoPaciente
from .filters import EgresoFilter

class IngresoViewSet(viewsets.ModelViewSet):
    queryset = Ingreso.objects.all()
    serializer_class = IngresoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

    @property
    def filterset_class(self):
        from .filters import IngresoFilter
        return IngresoFilter
    
    def get_queryset(self):
        all_ingresos = super().get_queryset()
        filtered_ingresos = all_ingresos
        user = self.request.user
        if user.is_authenticated:
            filtered_ingresos = all_ingresos.filter(medico__clinica=user.clinica)
        return filtered_ingresos

    @swagger_auto_schema(
        operation_summary="Crear Ingreso",
        operation_description=(
            "Crea un nuevo ingreso (pago de paciente). Puede asignarlo directamente a un TratamientoPaciente "
            "o proporcionando un 'paciente' para auto-asignar a los tratamientos pendientes."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['monto', 'medico', 'fecha_registro'],
            properties={
                'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='Monto del ingreso (requerido)'),
                'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del TratamientoPaciente (opcional)'),
                'medico': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del médico (requerido)'),
                'metodo': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    enum=['Efectivo', 'Tarjeta', 'Transferencia'],
                    description="Método de pago (default: 'Efectivo')"
                ),
                'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de registro (YYYY-MM-DD, requerido)'),
            },
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                    'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'medico': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'metodo': openapi.Schema(type=openapi.TYPE_STRING),
                    'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                },
            ),
            400: "Datos inválidos.",
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Listar Ingresos",
        operation_description="Obtiene la lista de ingresos filtrados por clínica del usuario autenticado. Soporta filtros y ordenamiento.",
        manual_parameters=[
            openapi.Parameter('paciente', openapi.IN_QUERY, description="ID del paciente", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('medico', openapi.IN_QUERY, description="ID del médico", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('tratamiento', openapi.IN_QUERY, description="ID del tratamiento", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('monto_min', openapi.IN_QUERY, description="Monto mínimo", type=openapi.TYPE_NUMBER, required=False),
            openapi.Parameter('monto_max', openapi.IN_QUERY, description="Monto máximo", type=openapi.TYPE_NUMBER, required=False),
            openapi.Parameter('created_date_after', openapi.IN_QUERY, description="Fecha creación desde (YYYY-MM-DD)", type=openapi.TYPE_STRING, format='date', required=False),
            openapi.Parameter('created_date_before', openapi.IN_QUERY, description="Fecha creación hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING, format='date', required=False),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Campo de ordenamiento (ej: '-created_at')", type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                    'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                    'results': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_OBJECT),
                    ),
                },
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Obtener Ingreso",
        operation_description="Obtiene los detalles de un ingreso específico por ID.",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                    'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'medico': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'metodo': openapi.Schema(type=openapi.TYPE_STRING),
                    'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                },
            ),
            404: "Ingreso no encontrado.",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Actualizar Ingreso",
        operation_description="Actualiza completamente un ingreso existente. No se recomienda cambiar el tratamientoPaciente después de creado.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['monto', 'medico', 'fecha_registro'],
            properties={
                'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='Monto del ingreso'),
                'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del TratamientoPaciente'),
                'medico': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del médico'),
                'metodo': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['Efectivo', 'Tarjeta', 'Transferencia'],
                    description="Método de pago"
                ),
                'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de registro (YYYY-MM-DD)'),
            },
        ),
        responses={
            200: openapi.Schema(type=openapi.TYPE_OBJECT),
            400: "Datos inválidos.",
            404: "Ingreso no encontrado.",
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Actualizar Parcialmente Ingreso",
        operation_description="Actualiza parcialmente un ingreso existente (solo campos proporcionados).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='Monto del ingreso (opcional)'),
                'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del TratamientoPaciente (opcional)'),
                'medico': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del médico (opcional)'),
                'metodo': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['Efectivo', 'Tarjeta', 'Transferencia'],
                    description="Método de pago (opcional)"
                ),
                'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de registro (opcional)'),
            },
        ),
        responses={
            200: openapi.Schema(type=openapi.TYPE_OBJECT),
            400: "Datos inválidos.",
            404: "Ingreso no encontrado.",
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Eliminar Ingreso",
        operation_description="Elimina un ingreso existente. Esto también puede afectar los egresos relacionados del médico.",
        responses={
            204: "Ingreso eliminado exitosamente.",
            404: "Ingreso no encontrado.",
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
class EgresoViewSet(viewsets.ModelViewSet):
    queryset = Egreso.objects.all()
    serializer_class = EgresoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = EgresoFilter  

    def get_queryset(self):
        all_egresos = super().get_queryset()
        filtered_egresos = all_egresos
        user = self.request.user
        if user.is_authenticated:
            filtered_egresos = all_egresos.filter(clinica=user.clinica)
        return filtered_egresos
    
    def perform_create(self, serializer):
        # Automatically set clinica from authenticated user
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'clinica'):
            serializer.save(clinica=user.clinica)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        # Ensure clinica remains the same as user's clinica on update
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'clinica'):
            serializer.save(clinica=user.clinica)
        else:
            serializer.save()

    @swagger_auto_schema(
        operation_summary="Crear Egreso",
        operation_description=(
            "Crea un nuevo egreso (gasto). Puede ser de tipo 'lab', 'odontologo' o 'clinica' dependiendo de si "
            "tiene tratamientoPaciente y/o medico asignado. La clínica se asigna automáticamente del usuario autenticado."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['monto', 'fecha_registro'],
            properties={
                'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='Monto del egreso (requerido)'),
                'medico': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del médico (opcional, null para gastos de lab/clinica)'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción del egreso (opcional)'),
                'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del TratamientoPaciente (opcional, para lab/odontologo)'),
                'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de registro (YYYY-MM-DD, requerido)'),
            },
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                    'medico': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                    'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                    'clinica': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                },
            ),
            400: "Datos inválidos.",
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Listar Egresos",
        operation_description="Obtiene la lista de egresos filtrados por clínica del usuario autenticado. Soporta filtros por tipo, monto y fechas.",
        manual_parameters=[
            openapi.Parameter('tipo_egreso', openapi.IN_QUERY, description="Tipo de egreso: 'lab', 'odontologo', 'clinica'", type=openapi.TYPE_STRING, enum=['lab', 'odontologo', 'clinica'], required=False),
            openapi.Parameter('monto_min', openapi.IN_QUERY, description="Monto mínimo", type=openapi.TYPE_NUMBER, required=False),
            openapi.Parameter('monto_max', openapi.IN_QUERY, description="Monto máximo", type=openapi.TYPE_NUMBER, required=False),
            openapi.Parameter('created_date_after', openapi.IN_QUERY, description="Fecha creación desde (YYYY-MM-DD)", type=openapi.TYPE_STRING, format='date', required=False),
            openapi.Parameter('created_date_before', openapi.IN_QUERY, description="Fecha creación hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING, format='date', required=False),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Campo de ordenamiento (ej: '-created_at')", type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                    'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                    'results': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_OBJECT),
                    ),
                },
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Obtener Egreso",
        operation_description="Obtiene los detalles de un egreso específico por ID.",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                    'medico': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                    'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                    'clinica': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                },
            ),
            404: "Egreso no encontrado.",
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Actualizar Egreso",
        operation_description="Actualiza completamente un egreso existente. La clínica se mantiene del usuario autenticado.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['monto', 'fecha_registro'],
            properties={
                'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='Monto del egreso'),
                'medico': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del médico (opcional)'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción del egreso (opcional)'),
                'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del TratamientoPaciente (opcional)'),
                'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de registro (YYYY-MM-DD)'),
            },
        ),
        responses={
            200: openapi.Schema(type=openapi.TYPE_OBJECT),
            400: "Datos inválidos.",
            404: "Egreso no encontrado.",
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Actualizar Parcialmente Egreso",
        operation_description="Actualiza parcialmente un egreso existente (solo campos proporcionados). La clínica se mantiene del usuario autenticado.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description='Monto del egreso (opcional)'),
                'medico': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del médico (opcional)'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción del egreso (opcional)'),
                'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del TratamientoPaciente (opcional)'),
                'fecha_registro': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de registro (opcional)'),
            },
        ),
        responses={
            200: openapi.Schema(type=openapi.TYPE_OBJECT),
            400: "Datos inválidos.",
            404: "Egreso no encontrado.",
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Eliminar Egreso",
        operation_description="Elimina un egreso existente. Si es de tipo 'lab', puede afectar los cálculos de egresos de odontólogos relacionados.",
        responses={
            204: "Egreso eliminado exitosamente.",
            404: "Egreso no encontrado.",
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
class CierreDeCajaApiView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Cierre de Caja (Close Cash Register)",
        operation_description=(
            "Retrieves the financial summary (Ingresos, Egresos, Balance) for a specific date or date range.\n\n"
            "- If no `date`, `start_date`, or `end_date` are provided, it defaults to **today**.\n"
            "- Optionally filter by `medico` or `paciente`.\n"
            "- Returns all relevant transactions grouped by date."
        ),
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Specific date (YYYY-MM-DD). Overrides start_date/end_date if provided.",
                type=openapi.TYPE_STRING,
                format='date',
                required=False,
            ),
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Start date for range (YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format='date',
                required=False,
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="End date for range (YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
                format='date',
                required=False,
            ),
            openapi.Parameter(
                'medico',
                openapi.IN_QUERY,
                description="Medico (doctor) ID to filter ingresos/egresos.",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                'paciente',
                openapi.IN_QUERY,
                description="Paciente ID to filter ingresos.",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                'group_by',
                openapi.IN_QUERY,
                description="Group ingresos by 'pacientes' (default) or 'metodo_pago'.",
                type=openapi.TYPE_STRING,
                enum=['pacientes', 'metodo_pago'],
                required=False,
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'ingresos': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'paciente': openapi.Schema(type=openapi.TYPE_STRING),
                                'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                                'medico': openapi.Schema(type=openapi.TYPE_STRING),
                                'metodo': openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        description="List of ingresos (income transactions).",
                    ),
                    'egresos': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                                'medico': openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        description="List of egresos (expenses).",
                    ),
                    'balance': openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description="Net balance."),
                },
                description="Financial summary result for the given period.",
            ),
            400: "Invalid date format or parameters.",
            500: "Internal server error.",
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            # --- Parse date parameters ---
            date_str = request.query_params.get('date')
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            medico_id = request.query_params.get('medico')
            paciente_id = request.query_params.get('paciente')
            group_by = request.query_params.get('group_by', 'pacientes') #option pacientes or metodo_pago

            today = datetime.now().date()

            if date_str:
                # If 'date' provided, use it as both start and end
                start_date = end_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            elif start_date_str and end_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            else:
                # Default to today
                start_date = end_date = today

            # --- Query ingresos ---
            ingresos_qs = Ingreso.objects.filter(created_at__date__range=(start_date, end_date))
            if medico_id:
                ingresos_qs = ingresos_qs.filter(medico_id=medico_id)
            if paciente_id:
                ingresos_qs = ingresos_qs.filter(tratamientoPaciente__paciente_id=paciente_id)

            total_ingresos = sum(ing.monto or 0.0 for ing in ingresos_qs)
            if group_by == 'pacientes':
                ingresos_data = [
                    {
                        'paciente': f"{i.tratamientoPaciente.paciente.nomb_pac} {i.tratamientoPaciente.paciente.apel_pac}"
                        if i.tratamientoPaciente else "Unknown",
                        'monto': i.monto,
                        'medico': str(i.medico) if i.medico else "Unknown",
                        'metodo': i.metodo,
                    }
                    for i in ingresos_qs
                ]
            else: #group_by metodo_pago
                ingresos_data = [
                    {
                        'metodo': 'efectivo',
                        'monto': sum(i.monto for i in ingresos_qs if i.metodo == 'efectivo'),
                    },
                    {
                        'metodo': 'tarjeta',
                        'monto': sum(i.monto for i in ingresos_qs if i.metodo == 'tarjeta'),
                    },
                    {
                        'metodo': 'transferencia',
                        'monto': sum(i.monto for i in ingresos_qs if i.metodo == 'transferencia'),
                    }
                ]
                 

            # --- Query egresos ---
            egresos_qs = Egreso.objects.filter(created_at__date__range=(start_date, end_date))
            if medico_id:
                egresos_qs = egresos_qs.filter(medico_id=medico_id)

            total_egresos = sum(egr.monto or 0.0 for egr in egresos_qs)
            egresos_data = [
                {
                    'monto': egr.monto,
                    'medico': str(egr.medico) if egr.medico else "Unknown",
                }
                for egr in egresos_qs
            ]

            # --- Final response ---
            data = {
                'ingresos': ingresos_data,
                'egresos': egresos_data,
                'total_ingresos': total_ingresos,
                'total_egresos': total_egresos,
                'balance': total_ingresos - total_egresos,
            }

            return Response(data, status=200)

        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
class DeudaPacienteApiView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Deuda de Paciente",
        operation_description=(
            "Obtiene el detalle de deuda de un paciente, incluyendo tratamientos, pagos realizados y totales.\n"
            "Requiere el parámetro de consulta 'paciente_id'."
        ),
        manual_parameters=[
            openapi.Parameter(
                'paciente_id',
                openapi.IN_QUERY,
                description="ID del paciente.",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'paciente': openapi.Schema(type=openapi.TYPE_STRING, description="Nombre completo del paciente"),
                    'tratamientos': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'tratamiento': openapi.Schema(type=openapi.TYPE_STRING),
                                'precio_base': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                                'descuento': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                                'descuento_porcentaje': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                                'monto_neto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                            },
                        ),
                        description="Tratamientos del paciente con montos calculados.",
                    ),
                    'pagos': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'monto': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                                'medico': openapi.Schema(type=openapi.TYPE_STRING),
                                'metodo': openapi.Schema(type=openapi.TYPE_STRING),
                                'fecha_pago': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                            },
                        ),
                        description="Pagos (ingresos) realizados por el paciente.",
                    ),
                    'deuda_neta': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                    'deuda_bruta': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                    'total_pagos': openapi.Schema(type=openapi.TYPE_NUMBER, format='float'),
                },
                description="Detalle de deuda del paciente.",
            ),
            400: "Parámetro 'paciente_id' faltante o formato inválido.",
            404: "Paciente no encontrado.",
            500: "Error interno del servidor.",
        }
    )
    def get(self, request, *args, **kwargs):
        paciente_id = request.query_params.get('paciente_id')
        if not paciente_id:
            return Response({'error': 'paciente_id parameter is required.'}, status=400)

        paciente = Paciente.objects.filter(id=paciente_id).first()
        if not paciente:
            return Response({'error': 'Paciente not found.'}, status=404)
        
        try:
            
            data = {
                'paciente': f"{paciente.nomb_pac} {paciente.apel_pac}",
                'tratamientos': [],
                'pagos': [],
                'deuda_neta': 0.0,
                'deuda_bruta': 0.0,
                'total_pagos': 0.0,
            }
            tratamientos = TratamientoPaciente.objects.filter(paciente_id=paciente_id)
            deuda_bruta = 0.0
            for tp in tratamientos:
                deuda_bruta += tp.monto_neto()
                data['tratamientos'].append({
                    'id': tp.id,
                    'tratamiento': tp.tratamiento.nombre,
                    'precio_base': tp.tratamiento.precioBase,
                    'descuento': tp.descuento,
                    'descuento_porcentaje': tp.descuento_porcentaje,
                    'monto_neto': tp.monto_neto(),
                })

            ingresos = Ingreso.objects.filter(tratamientoPaciente__paciente_id=paciente_id)
            total_ingresos = sum(ing.monto or 0.0 for ing in ingresos)

            for ing in ingresos:
                data['pagos'].append({
                    'id': ing.id,
                    'monto': ing.monto,
                    'medico': str(ing.medico) if ing.medico else "Unknown",
                    'metodo': ing.metodo,
                    'fecha_pago': ing.fecha_registro,
                })

            data['deuda_neta'] = deuda_bruta - total_ingresos
            data['deuda_bruta'] = deuda_bruta
            data['total_pagos'] = total_ingresos

            return Response(data, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)