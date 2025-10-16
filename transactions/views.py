from rest_framework import filters, viewsets
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import (
    Ingreso, Egreso
)
from .serializers import (
    IngresoSerializer,
)
# Add drf_yasg imports for schema docs
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from datetime import datetime

# Add explicit request schemas for the serializer input (serializer accepts 'paciente' id write-only)
INGRESO_CREATE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'monto': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount to allocate (required)'),
        'paciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='Paciente ID to auto-allocate across unpaid tratamientos (write-only, optional)'),
        'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='TratamientoPaciente ID to assign the ingreso (optional)'),
        'medico': openapi.Schema(type=openapi.TYPE_INTEGER, description='Medico user ID (required)'),
        'metodo': openapi.Schema(type=openapi.TYPE_STRING, description="Payment method, e.g. 'Efectivo'"),
    },
    required=['monto', 'medico'],
    description="Create Ingreso. Provide either 'paciente' (to auto-allocate across unpaid TratamientoPaciente) OR 'tratamientoPaciente' to assign to a single tratamiento."
)

INGRESO_UPDATE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'monto': openapi.Schema(type=openapi.TYPE_NUMBER, description='New amount (optional)'),
        'tratamientoPaciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='Assign/replace tratamientoPaciente (optional)'),
        'medico': openapi.Schema(type=openapi.TYPE_INTEGER, description='Medico user ID (optional)'),
        'metodo': openapi.Schema(type=openapi.TYPE_STRING, description='Payment method (optional)'),
        # Note: 'paciente' is intentionally omitted because reallocation via update is not supported.
    },
    description="Update Ingreso. Do NOT supply 'paciente' here — reallocation is not supported on update; create a new ingreso instead."
)

PACIENTE_QUERY_PARAM = openapi.Parameter(
    name='paciente',
    in_=openapi.IN_QUERY,
    description='Filter list by paciente id (matches ingresos allocated via paciente allocation)',
    type=openapi.TYPE_INTEGER,
)

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

    @swagger_auto_schema(
        request_body=INGRESO_CREATE_SCHEMA,
        responses={201: IngresoSerializer},
        operation_description="Create an Ingreso. If 'paciente' (ID) is provided and 'tratamientoPaciente' is omitted, the provided monto will be auto-allocated across oldest unpaid TratamientoPaciente records for that paciente."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        manual_parameters=[
            PACIENTE_QUERY_PARAM,
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Ordering fields", type=openapi.TYPE_STRING),
        ],
        responses={200: IngresoSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={200: IngresoSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=INGRESO_UPDATE_SCHEMA,
        responses={200: IngresoSerializer},
        operation_description="Update an Ingreso. 'paciente' is not supported here; to reallocate create a new ingreso."
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=INGRESO_UPDATE_SCHEMA,
        responses={200: IngresoSerializer},
        operation_description="Partial update. 'paciente' is not supported on partial updates."
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={204: 'No Content'}
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
                    'medico': egr.medico.username if egr.medico else "Unknown",
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
