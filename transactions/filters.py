import django_filters
from .models import (
    Ingreso
)
from django.db.models.functions import TruncDate


class IngresoFilter(django_filters.FilterSet):
    paciente = django_filters.NumberFilter(field_name='paciente_id', lookup_expr='exact')

    monto_min = django_filters.NumberFilter(field_name='monto', lookup_expr='gte')
    monto_max = django_filters.NumberFilter(field_name='monto', lookup_expr='lte')

    # Filter by date (YYYY-MM-DD) using the date part of created_at
    created_date_after = django_filters.DateFilter(method='filter_created_after')
    created_date_before = django_filters.DateFilter(method='filter_created_before')

    class Meta:
        model = Ingreso
        # we list the public filter names, not the internal field paths
        fields = ['paciente', 'monto_min', 'monto_max', 'created_date_after', 'created_date_before']

    def filter_created_after(self, queryset, name, value):
        # value is a date; compare on the date portion of created_at
        return queryset.annotate(cdate=TruncDate('created_at')).filter(cdate__gte=value)

    def filter_created_before(self, queryset, name, value):
        return queryset.annotate(cdate=TruncDate('created_at')).filter(cdate__lte=value)