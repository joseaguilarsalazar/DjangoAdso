from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Paciente


from .models import (
    Odontograma, 
    Diente, 
    DienteOdontograma, 
    CasoMultidental,
    )

from .serializers import (
    OdontogramaSerializer, 
    DienteSerializer, 
    DienteOdontogramaSerializer, 
    CasoMultidentalSerializer,
    )

from .filters import (
    OdontogramaFilter, 
    DienteFilter, 
    DienteOdontogramaFilter, 
    CasoMultidentalFilter,
    )
# Create your views here.


class OdontogramaViewSet(viewsets.ModelViewSet):
    queryset = Odontograma.objects.all().order_by('id')
    serializer_class = OdontogramaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OdontogramaFilter
    ordering_fields = '__all__'

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        paciente_nombre = request.query_params.get('paciente_nombre')

        if paciente_nombre:
            pacientes = Paciente.objects.all()
            concidences = [p for p in pacientes if paciente_nombre.lower() in str(p.__str__()).lower()]
            return_list = []

            for paciente in concidences:
                odontograma = Odontograma.objects.filter(paciente_id=paciente.id).first()
                if odontograma:
                    return_list.append(odontograma)

            serializer = self.get_serializer(return_list, many=True)
            return Response(serializer.data)

        return super().list(request, *args, **kwargs)

class DienteViewSet(viewsets.ModelViewSet):
    queryset = Diente.objects.all().order_by('id')
    serializer_class = DienteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = DienteFilter
    ordering_fields = '__all__'

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated()]


class DienteOdontogramaViewSet(viewsets.ModelViewSet):
    queryset = DienteOdontograma.objects.all().order_by('id')
    serializer_class = DienteOdontogramaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = DienteOdontogramaFilter
    ordering_fields = '__all__'

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated()]


class CasoMultidentalViewSet(viewsets.ModelViewSet):
    queryset = CasoMultidental.objects.all().order_by('id')
    serializer_class = CasoMultidentalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CasoMultidentalFilter
    ordering_fields = '__all__'

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated()]