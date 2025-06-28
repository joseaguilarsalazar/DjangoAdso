import django_filters
from .models import (
    Odontograma, 
    Diente, 
    DienteOdontograma, 
    CasoMultidental
    )


class OdontogramaFilter(django_filters.FilterSet):
    paciente_id = django_filters.NumberFilter(field_name="paciente__id")

    class Meta:
        model = Odontograma
        fields = ['paciente_id']


class DienteFilter(django_filters.FilterSet):
    numero = django_filters.NumberFilter(field_name="numeroDiente")

    class Meta:
        model = Diente
        fields = ['numeroDiente']


class DienteOdontogramaFilter(django_filters.FilterSet):
    odontograma_id = django_filters.NumberFilter(field_name="odontograma__id")
    diente_id = django_filters.NumberFilter(field_name="diente__id")

    class Meta:
        model = DienteOdontograma
        fields = ['odontograma_id', 'diente_id']


class CasoMultidentalFilter(django_filters.FilterSet):
    odontograma_id = django_filters.NumberFilter(field_name="odontograma__id")
    diente1 = django_filters.NumberFilter(field_name="dienteExtremo1__id")
    diente2 = django_filters.NumberFilter(field_name="dienteExtremo2__id")
    caso = django_filters.CharFilter(field_name="caso", lookup_expr='iexact')

    class Meta:
        model = CasoMultidental
        fields = ['odontograma_id', 'diente1', 'diente2', 'caso']
