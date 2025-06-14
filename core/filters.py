import django_filters
from .models import Historial, Tratamiento, Especialidad, Cita, Pagos, Paciente

class PacienteFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    tipo_doc = django_filters.CharFilter()
    num_doc = django_filters.CharFilter()
    sexo = django_filters.ChoiceFilter(choices=Paciente._meta.get_field('sexo').choices)
    fecha_nac__gte = django_filters.DateFilter(field_name='fecha_nac', lookup_expr='gte')
    fecha_nac__lte = django_filters.DateFilter(field_name='fecha_nac', lookup_expr='lte')

    class Meta:
        model = Paciente
        fields = ['tipo_doc', 'num_doc', 'nombre', 'sexo', 'fecha_nac__gte', 'fecha_nac__lte']


class HistorialFilter(django_filters.FilterSet):
    class Meta:
        model = Historial
        fields = {
            'id_paciente': ['exact'],
            'trata_medic': ['exact'],
            'propen_hemo': ['exact'],
            'alergico': ['exact'],
            'hipertenso': ['exact'],
            'diabetico': ['exact'],
            'embarazada': ['exact'],
            'created_at': ['date__gte', 'date__lte'],
        }

class TratamientoFilter(django_filters.FilterSet):
    class Meta:
        model = Tratamiento
        fields = {
            'tratamiento': ['icontains'],
            'precio': ['gte', 'lte'],
        }

class EspecialidadFilter(django_filters.FilterSet):
    class Meta:
        model = Especialidad
        fields = {
            'descripcion': ['icontains'],
        }


class CitaFilter(django_filters.FilterSet):
    class Meta:
        model = Cita
        fields = {
            'tratamiento': ['exact'],
            'medico': ['exact'],
            'paciente': ['exact'],
            'fecha': ['gte', 'lte'],
            'estadoCita': ['exact'],
            'estadoPago': ['exact'],
        }

class PagosFilter(django_filters.FilterSet):
    class Meta:
        model = Pagos
        fields = {
            'cita': ['exact'],
            'paciente': ['exact'],
            'monto': ['gte', 'lte'],
            'created_at': ['date__gte', 'date__lte'],
        }
