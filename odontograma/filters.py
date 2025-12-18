import django_filters
from .models import (
    Odontograma, 
    Diente, 
    CasoMultidental,
    Hallazgo
    )


class OdontogramaFilter(django_filters.FilterSet):
    paciente_id = django_filters.NumberFilter(field_name="paciente__id")

    class Meta:
        model = Odontograma
        fields = ['paciente_id']


class DienteFilter(django_filters.FilterSet):
    numero = django_filters.NumberFilter(field_name="numero")

    class Meta:
        model = Diente
        fields = ['numero']

class CasoMultidentalFilter(django_filters.FilterSet):
    odontograma_id = django_filters.NumberFilter(field_name="odontograma__id")
    diente1 = django_filters.NumberFilter(field_name="dienteExtremo1__id")
    diente2 = django_filters.NumberFilter(field_name="dienteExtremo2__id")
    caso = django_filters.CharFilter(field_name="caso", lookup_expr='iexact')
    
    paciente_id = django_filters.NumberFilter(field_name="odontograma__paciente__id")
    class Meta:
        model = CasoMultidental
        fields = ['odontograma_id', 'diente1', 'diente2', 'caso', 'paciente_id']


class HallazgoFilter(django_filters.FilterSet):
    odontograma_id = django_filters.NumberFilter(field_name="odontograma__id")
    diente_numero = django_filters.NumberFilter(field_name="diente__numero")
    
    class Meta:
        model = Hallazgo
        fields = ['odontograma_id', 'diente_numero']