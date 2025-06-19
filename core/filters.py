import django_filters
from .models import (
    Historial, 
    Tratamiento, 
    Especialidad, 
    Cita, 
    Pagos, 
    Paciente,
    Clinica,
    Alergia,
    PacienteAlergia,
    Banco,
    Categoria,
    PacienteTratamiento,
    Enfermedad,
    PacienteEvolucion,
    PacienteEnfermedad,)

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
            'pacienteTratamiento': ['exact'],
            'paciente': ['exact'],
            'monto': ['gte', 'lte'],
            'created_at': ['date__gte', 'date__lte'],
        }


class EnfermedadFilter(django_filters.FilterSet):
    descripcion = django_filters.CharFilter(lookup_expr='icontains')
    estado = django_filters.CharFilter()

    class Meta:
        model = Enfermedad
        fields = ['descripcion', 'estado']


class PacienteEvolucionFilter(django_filters.FilterSet):
    paciente = django_filters.NumberFilter(field_name='paciente__id')
    especialidad = django_filters.NumberFilter(field_name='especialidad__id')
    medico = django_filters.NumberFilter(field_name='medico__id')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = PacienteEvolucion
        fields = ['paciente', 'especialidad', 'medico', 'created_at']


class PacienteEnfermedadFilter(django_filters.FilterSet):
    paciente = django_filters.NumberFilter(field_name='paciente__id')
    enfermedad = django_filters.NumberFilter(field_name='enfermedad__id')

    class Meta:
        model = PacienteEnfermedad
        fields = ['paciente', 'enfermedad']


class PacienteTratamientoFilter(django_filters.FilterSet):
    paciente = django_filters.NumberFilter(field_name='paciente__id')
    tratamiento = django_filters.NumberFilter(field_name='tratamiento__id')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = PacienteTratamiento
        fields = ['paciente', 'tratamiento', 'created_at']


class CategoriaFilter(django_filters.FilterSet):
    nomb_cat = django_filters.CharFilter(lookup_expr='icontains')
    esta_cat = django_filters.CharFilter()

    class Meta:
        model = Categoria
        fields = ['nomb_cat', 'esta_cat']


class AlergiaFilter(django_filters.FilterSet):
    nombre_ale = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Alergia
        fields = ['nombre_ale']


class PacienteAlergiaFilter(django_filters.FilterSet):
    paciente = django_filters.NumberFilter(field_name='paciente__id')
    alergia = django_filters.NumberFilter(field_name='alergia__id')
    observacion = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = PacienteAlergia
        fields = ['paciente', 'alergia', 'observacion']


class BancoFilter(django_filters.FilterSet):
    descripcion = django_filters.CharFilter(lookup_expr='icontains')
    estado = django_filters.NumberFilter()

    class Meta:
        model = Banco
        fields = ['descripcion', 'estado']

class ClinicaFilter(django_filters.FilterSet):
    nomb_clin = django_filters.CharFilter(lookup_expr='icontains')
    direc_clin = django_filters.CharFilter(lookup_expr='icontains')
    email_clin = django_filters.CharFilter(lookup_expr='icontains')
    ruc_clin = django_filters.CharFilter(lookup_expr='icontains')
    cod_plan = django_filters.NumberFilter()
    esta_clin = django_filters.CharFilter()
    fecha_clin = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Clinica
        fields = [
            'nomb_clin', 'direc_clin', 'email_clin', 'ruc_clin',
            'cod_plan', 'esta_clin', 'fecha_clin'
        ]