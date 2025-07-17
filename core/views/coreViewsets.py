from rest_framework import viewsets, views
from django.contrib.auth import get_user_model
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from ..models import (
    Paciente,
    Historial, 
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
)
from ..serializers import (
    PacienteSerializer,
    HistorialSerializer, TratamientoSerializer, EspecialidadSerializer, 
    CitaSerializer, UserSerializer,
    ClinicaSerializer,
    AlergiaSerializer,
    PacienteAlergiaSerializer,
    BancoSerializer,
    CategoriaSerializer,
    EnfermedadSerializer,
    PacienteEvolucionSerializer,
    PacienteEnfermedadSerializer,
)
from ..filters import (
    HistorialFilter, TratamientoFilter, EspecialidadFilter,
     CitaFilter, PacienteFilter,
     ClinicaFilter,
    AlergiaFilter,
    PacienteAlergiaFilter,
    BancoFilter,
    CategoriaFilter,
    EnfermedadFilter,
    PacienteEvolucionFilter,
    PacienteEnfermedadFilter,
)

User = get_user_model()

class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all().order_by('id')
    serializer_class = PacienteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PacienteFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]


class HistorialViewSet(viewsets.ModelViewSet):
    queryset = Historial.objects.all()
    serializer_class = HistorialSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = HistorialFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class TratamientoViewSet(viewsets.ModelViewSet):
    queryset = Tratamiento.objects.all()
    serializer_class = TratamientoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TratamientoFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = EspecialidadFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CitaFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class ClinicaViewSet(viewsets.ModelViewSet):
    queryset = Clinica.objects.all()
    serializer_class = ClinicaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClinicaFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class AlergiaViewSet(viewsets.ModelViewSet):
    queryset = Alergia.objects.all()
    serializer_class = AlergiaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AlergiaFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class PacienteAlergiaViewSet(viewsets.ModelViewSet):
    queryset = PacienteAlergia.objects.all()
    serializer_class = PacienteAlergiaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PacienteAlergiaFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class BancoViewSet(viewsets.ModelViewSet):
    queryset = Banco.objects.all()
    serializer_class = BancoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BancoFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoriaFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class EnfermedadViewSet(viewsets.ModelViewSet):
    queryset = Enfermedad.objects.all()
    serializer_class = EnfermedadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EnfermedadFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]


class PacienteEvolucionViewSet(viewsets.ModelViewSet):
    queryset = PacienteEvolucion.objects.all()
    serializer_class = PacienteEvolucionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PacienteEvolucionFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]


class PacienteEnfermedadViewSet(viewsets.ModelViewSet):
    queryset = PacienteEnfermedad.objects.all()
    serializer_class = PacienteEnfermedadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PacienteEnfermedadFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]