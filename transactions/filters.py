import django_filters
from .models import (
    Ingreso
)
from django.db.models.functions import TruncDate


class IngresoFilter(django_filters.FilterSet):
    # filter by paciente (going through tratamientoPaciente → paciente)
    paciente = django_filters.NumberFilter(
        field_name='tratamientoPaciente__paciente_id',
        lookup_expr='exact'
    )

    # filter by medico (direct FK to User)
    medico = django_filters.NumberFilter(
        field_name='medico_id',
        lookup_expr='exact'
    )

    # filter by tratamiento (through tratamientoPaciente → tratamiento)
    tratamiento = django_filters.NumberFilter(
        field_name='tratamientoPaciente__tratamiento_id',
        lookup_expr='exact'
    )

    monto_min = django_filters.NumberFilter(field_name='monto', lookup_expr='gte')
    monto_max = django_filters.NumberFilter(field_name='monto', lookup_expr='lte')

    created_date_after = django_filters.DateFilter(method='filter_created_after')
    created_date_before = django_filters.DateFilter(method='filter_created_before')

    class Meta:
        model = Ingreso
        fields = [
            'paciente',
            'medico',
            'tratamiento',
            'monto_min',
            'monto_max',
            'created_date_after',
            'created_date_before',
        ]

    def filter_created_after(self, queryset, name, value):
        return queryset.annotate(cdate=TruncDate('created_at')).filter(cdate__gte=value)

    def filter_created_before(self, queryset, name, value):
        return queryset.annotate(cdate=TruncDate('created_at')).filter(cdate__lte=value)