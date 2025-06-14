# your_app/views.py
from rest_framework import viewsets
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Historial, Paciente
from .serializers import PacienteSerializer, HistorialSerializer
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import (
    Historial, Tratamiento, Especialidad, Cita, Pagos
)
from .serializers import (
    HistorialSerializer, TratamientoSerializer, EspecialidadSerializer, 
    CitaSerializer, PagosSerializer
)
from .filters import (
    HistorialFilter, TratamientoFilter, EspecialidadFilter,
     CitaFilter, PagosFilter
)

User = get_user_model()


class PacienteViewSet(viewsets.ModelViewSet):
    """
    Endpoints para /api/pacientes/
    Filtra por rol='Paciente' y opcional ?q= para buscar num_doc o name.
    """
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer


class HistorialViewSet(viewsets.ModelViewSet):
    queryset = Historial.objects.all()
    serializer_class = HistorialSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = HistorialFilter
    ordering_fields = '__all__'

class TratamientoViewSet(viewsets.ModelViewSet):
    queryset = Tratamiento.objects.all()
    serializer_class = TratamientoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TratamientoFilter
    ordering_fields = '__all__'

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = EspecialidadFilter
    ordering_fields = '__all__'

class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CitaFilter
    ordering_fields = '__all__'

class PagosViewSet(viewsets.ModelViewSet):
    queryset = Pagos.objects.all()
    serializer_class = PagosSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PagosFilter
    ordering_fields = '__all__'


@api_view(['POST'])
def cargar_costo(request):
    tratamiento_id = request.data.get('tratamiento')
    try:
        tratamiento = Tratamiento.objects.get(id=tratamiento_id)
        return Response({'costo': tratamiento.precio})
    except Tratamiento.DoesNotExist:
        return Response({'error': 'Tratamiento no encontrado'}, status=404)
    
@api_view(['POST'])
def buscar_paciente(request):
    paciente_id = request.data.get('paciente')
    try:
        paciente = Paciente.objects.get(id=paciente_id)
        return Response({'nombres': paciente.name.upper()})
    except Paciente.DoesNotExist:
        return Response({'error': 'Paciente no encontrado'}, status=404)


@api_view(['POST'])
def validar_documento(request):
    numero = request.data.get('numero')
    correo = request.data.get('correo')

    docu = 'Si' if Paciente.objects.filter(NumDoc=numero).exists() else 'No'
    email = 'Si' if Paciente.objects.filter(email=correo).exists() else 'No'

    return Response({'docu': docu, 'correo': email})

@api_view(['POST'])
def validar_dni(request):
    numero = request.data.get('numero')
    existe = 'Si' if User.objects.filter(num_doc=numero).exists() else 'No'
    return Response({'datos': existe})


@api_view(['GET'])
def cargar_calendario(request):
    eventos = []
    citas = Cita.objects.select_related('paciente', 'tratamiento').all()

    for cita in citas:
        paciente = cita.paciente.name.upper()
        tratamiento = cita.tratamiento.tratamiento
        color = '#C92417' if cita.estadoCita == 'Asignado' else '#539B0A'
        eventos.append({
            'paciente': paciente,
            'tratamiento': tratamiento,
            'enfermedad': cita.enfermedad,
            'fecha': f"{cita.fecha} {cita.hora}",
            'color': color,
        })
    return Response({'datos': eventos})

@api_view(['POST'])
def buscar_dni(request):
    dni = request.data.get('dni')
    pacientes = Paciente.objects.filter(NumDoc=dni)
    serializer = PacienteSerializer(pacientes, many=True)
    return Response({'datos': serializer.data})


@api_view(['POST'])
def validar_registro(request):
    paciente_id = request.data.get('idpaciente')
    fecha = request.data.get('fecha')
    hora = request.data.get('hora')

    ultima_cita = Cita.objects.filter(paciente_id=paciente_id, fecha=fecha).order_by('-id').first()
    rango = 100

    if ultima_cita:
        from datetime import datetime
        nueva_fecha = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        ultima_fecha = datetime.combine(ultima_cita.fecha, ultima_cita.hora)
        rango = abs(int((nueva_fecha - ultima_fecha).total_seconds() // 3600))

    return Response({'rango': rango})
