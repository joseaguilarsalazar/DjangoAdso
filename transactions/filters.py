import django_filters
from .models import (
    Ingreso,
    Egreso
)
from django.db.models.functions import TruncDate
from django.db.models import Q


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
    

class EgresoFilter(django_filters.FilterSet):
    monto_min = django_filters.NumberFilter(field_name='monto', lookup_expr='gte')
    monto_max = django_filters.NumberFilter(field_name='monto', lookup_expr='lte')
    tipo_egreso = django_filters.CharFilter(method='filter_tipo_egreso')
    fecha_registro = django_filters.DateFilter(field_name='fecha_registro', lookup_expr='exact')

    created_date_after = django_filters.DateFilter(method='filter_created_after')
    created_date_before = django_filters.DateFilter(method='filter_created_before')

    class Meta:
        model = Egreso
        fields = [
            'monto_min',
            'monto_max',
            'tipo_egreso',
            'fecha_registro',
            'created_date_after',
            'created_date_before',
        ]

    def filter_created_after(self, queryset, name, value):
        return queryset.annotate(cdate=TruncDate('created_at')).filter(cdate__gte=value)

    def filter_created_before(self, queryset, name, value):
        return queryset.annotate(cdate=TruncDate('created_at')).filter(cdate__lte=value)
    
    def filter_tipo_egreso(self, queryset, name, value):
        """
        Filter based on tipoEgreso logic:
        - 'odontologo': tratamientoPaciente is not null AND medico is not null
        - 'lab': tratamientoPaciente is not null AND medico is null
        - 'clinica': tratamientoPaciente is null (medico may or may not be null)
        """
        value_lower = value.lower()
        
        if value_lower == 'odontologo':
            return queryset.filter(
                tratamientoPaciente__isnull=False,
                medico__isnull=False
            )
        elif value_lower == 'lab':
            return queryset.filter(
                tratamientoPaciente__isnull=False,
                medico__isnull=True
            )
        elif value_lower == 'clinica':
            return queryset.filter(tratamientoPaciente__isnull=True)
        else:
            # If invalid value, return unfiltered queryset
            return queryset