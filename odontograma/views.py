from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend


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
    permission_classes = [AllowAny]

class DienteViewSet(viewsets.ModelViewSet):
    queryset = Diente.objects.all().order_by('id')
    serializer_class = DienteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = DienteFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class DienteOdontogramaViewSet(viewsets.ModelViewSet):
    queryset = DienteOdontograma.objects.all().order_by('id')
    serializer_class = DienteOdontogramaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = DienteOdontogramaFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

class CasoMultidentalViewSet(viewsets.ModelViewSet):
    queryset = CasoMultidental.objects.all().order_by('id')
    serializer_class = CasoMultidentalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CasoMultidentalFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]