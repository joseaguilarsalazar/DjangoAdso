from rest_framework import viewsets
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from .models import (
    Pagos,
)
from .serializers import (
    PagosSerializer,
)
from .filters import (
    PagosFilter,
)
# Create your views here.

class PagosViewSet(viewsets.ModelViewSet):
    queryset = Pagos.objects.all()
    serializer_class = PagosSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PagosFilter
    ordering_fields = '__all__'
    permission_classes = [AllowAny]

    