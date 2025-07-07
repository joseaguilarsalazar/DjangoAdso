import django_filters
from .models import (
    Pagos
)


class PagosFilter(django_filters.FilterSet):
    class Meta:
        model = Pagos
        fields = {
            'pacienteTratamiento': ['exact'],
            'paciente': ['exact'],
            'monto': ['gte', 'lte'],
            'created_at': ['date__gte', 'date__lte'],
        }