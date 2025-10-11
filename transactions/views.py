from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import (
    Ingreso,
)
from .serializers import (
    IngresoSerializer,
)
# Add drf_yasg imports for schema docs
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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

