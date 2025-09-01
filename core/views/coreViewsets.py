from rest_framework import viewsets, views
from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from ..models import (
    Paciente,
    Tratamiento, 
    Especialidad, 
    Cita,
    Clinica,
    Alergia,
    PacienteAlergia,
    Banco,
    Categoria,
    Enfermedad,
    PacienteEvolucion,
    PacienteEnfermedad,
    PacienteDiagnostico,
    PacientePlaca,
)
from ..serializers import (
    PacienteSerializer,
    TratamientoSerializer, EspecialidadSerializer, 
    CitaSerializer, UserSerializer,
    ClinicaSerializer,
    AlergiaSerializer,
    PacienteAlergiaSerializer,
    BancoSerializer,
    CategoriaSerializer,
    EnfermedadSerializer,
    PacienteEvolucionSerializer,
    PacienteEnfermedadSerializer,
    PacienteDiagnosticoSerializer,
    PacientePlacaSerializer,
    )
from ..filters import (
    TratamientoFilter, EspecialidadFilter,
     CitaFilter, PacienteFilter,
     ClinicaFilter,
    AlergiaFilter,
    PacienteAlergiaFilter,
    BancoFilter,
    CategoriaFilter,
    EnfermedadFilter,
    PacienteEvolucionFilter,
    PacienteEnfermedadFilter,
    PacienteDiagnosticoFilter,
    PacientePlacaFilter,
    UserFilter
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = UserFilter
    serializer_class = UserSerializer
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

    # ---------------------------
    # Create (POST /users/)
    # ---------------------------
    @swagger_auto_schema(
        operation_summary="Crear un usuario",
        operation_description=(
            "Crea un usuario. **Para crear** un usuario con contraseña, debe enviar **password** y **password2** "
            "y ambos deben coincidir. El campo `password` es write-only y no se devuelve en la respuesta.\n\n"
            "Si no envía contraseña, se creará con contraseña no usable (no podrá iniciar sesión hasta establecerla)."
        ),
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description="Usuario creado correctamente",
                schema=UserSerializer()
            ),
            400: openapi.Response(description="Error de validación (p. ej. contraseñas no coinciden)"),
            401: openapi.Response(description="No autorizado"),
        }
    )
    def create(self, request, *args, **kwargs):
        """
        create: usado por drf ModelViewSet para crear usuarios.
        La lógica real de hashing de contraseña está en UserSerializer.create().
        """
        return super().create(request, *args, **kwargs)

    # ---------------------------
    # Full update (PUT /users/{pk}/)
    # ---------------------------
    @swagger_auto_schema(
        operation_summary="Actualizar un usuario (reemplazo completo)",
        operation_description=(
            "Actualiza todos los campos de un usuario. Si desea cambiar la contraseña, incluya **password** y **password2** "
            "y asegúrese de que coincidan. Si omite `password`, la contraseña permanecerá sin cambios."
        ),
        request_body=UserSerializer,
        responses={
            200: openapi.Response(
                description="Usuario actualizado correctamente",
                schema=UserSerializer()
            ),
            400: openapi.Response(description="Error de validación"),
            401: openapi.Response(description="No autorizado"),
            404: openapi.Response(description="Usuario no encontrado"),
        }
    )
    def update(self, request, *args, **kwargs):
        """
        update: sobrescribe el registro completo. La lógica de set_password está en UserSerializer.update().
        """
        return super().update(request, *args, **kwargs)

    # ---------------------------
    # Partial update (PATCH /users/{pk}/)
    # ---------------------------
    @swagger_auto_schema(
        operation_summary="Actualizar parcialmente un usuario",
        operation_description=(
            "Actualiza solo los campos enviados. Para cambiar contraseña envíe **password** y **password2** juntos. "
            "Si cambia otros campos, puede enviar únicamente los que desea modificar."
        ),
        request_body=UserSerializer,
        responses={
            200: openapi.Response(
                description="Usuario parcialmente actualizado",
                schema=UserSerializer()
            ),
            400: openapi.Response(description="Error de validación"),
            401: openapi.Response(description="No autorizado"),
            404: openapi.Response(description="Usuario no encontrado"),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """
        partial_update: maneja cambios parciales; la verificación de password/password2 también ocurre en el serializer.
        """
        return super().partial_update(request, *args, **kwargs)

class PacienteViewSet(viewsets.ModelViewSet):
    serializer_class = PacienteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PacienteFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Paciente.objects.all()

        # Example: filter by medico assigned to the paciente
        if user.is_authenticated:
            queryset = queryset.filter(clinica=user.clinica)

        return queryset

class TratamientoViewSet(viewsets.ModelViewSet):
    queryset = Tratamiento.objects.all()
    serializer_class = TratamientoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TratamientoFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = EspecialidadFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

class CitaViewSet(viewsets.ModelViewSet):
    serializer_class = CitaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CitaFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        # Start with all citas
        qs = Cita.objects.all()

        # Restrict by clinica if authenticated
        if user.is_authenticated and hasattr(user, "clinica"):
            qs = qs.filter(paciente__clinica=user.clinica)

        return qs

class ClinicaViewSet(viewsets.ModelViewSet):
    queryset = Clinica.objects.all()
    serializer_class = ClinicaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClinicaFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

class AlergiaViewSet(viewsets.ModelViewSet):
    queryset = Alergia.objects.all()
    serializer_class = AlergiaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AlergiaFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

class PacienteAlergiaViewSet(viewsets.ModelViewSet):
    queryset = PacienteAlergia.objects.all()
    serializer_class = PacienteAlergiaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PacienteAlergiaFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

class BancoViewSet(viewsets.ModelViewSet):
    queryset = Banco.objects.all()
    serializer_class = BancoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BancoFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoriaFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

class EnfermedadViewSet(viewsets.ModelViewSet):
    queryset = Enfermedad.objects.all()
    serializer_class = EnfermedadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EnfermedadFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]


class PacienteEvolucionViewSet(viewsets.ModelViewSet):
    queryset = PacienteEvolucion.objects.all()
    serializer_class = PacienteEvolucionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PacienteEvolucionFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]


class PacienteEnfermedadViewSet(viewsets.ModelViewSet):
    queryset = PacienteEnfermedad.objects.all()
    serializer_class = PacienteEnfermedadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PacienteEnfermedadFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

class PacienteDiagnosticoViewSet(viewsets.ModelViewSet):
    queryset = PacienteDiagnostico.objects.all()
    serializer_class = PacienteDiagnosticoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PacienteDiagnosticoFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

class PacientePlacaViewSet(viewsets.ModelViewSet):
    queryset = PacientePlaca.objects.all()
    serializer_class = PacientePlacaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PacientePlacaFilter
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]