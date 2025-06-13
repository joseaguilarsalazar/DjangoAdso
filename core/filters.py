import django_filters
from .models import Historial, Tratamiento, Especialidad, Medico, Cita, Pagos

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

class MedicoFilter(django_filters.FilterSet):
    class Meta:
        model = Medico
        fields = {
            'nombres': ['icontains'],
            'apellidos': ['icontains'],
            'DNI': ['exact'],
            'especialidad': ['exact'],
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
