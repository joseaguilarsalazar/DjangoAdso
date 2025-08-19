from rest_framework import viewsets
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import (
    Ingreso,
)
from .serializers import (
    IngresoSerializer,
)
# Create your views here.

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

    