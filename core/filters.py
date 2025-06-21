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
    nomb_pac = django_filters.CharFilter(lookup_expr='icontains')
    apel_pac = django_filters.CharFilter(lookup_expr='icontains')
    edad_pac = django_filters.CharFilter(lookup_expr='exact')
    ocupacion = django_filters.CharFilter(lookup_expr='icontains')
    lugar_nacimiento = django_filters.CharFilter(lookup_expr='icontains')
    informacion_clinica = django_filters.CharFilter(lookup_expr='icontains')
    dire_pac = django_filters.CharFilter(lookup_expr='icontains')
    telf_pac = django_filters.CharFilter(lookup_expr='icontains')
    dni_pac = django_filters.CharFilter(lookup_expr='icontains')
    fena_pac = django_filters.DateFromToRangeFilter()
    fecha_registro = django_filters.DateTimeFromToRangeFilter()
    civi_pac = django_filters.CharFilter(lookup_expr='exact')
    afil_pac = django_filters.CharFilter(lookup_expr='icontains')
    aler_pac = django_filters.CharFilter(lookup_expr='icontains')
    emai_pac = django_filters.CharFilter(lookup_expr='icontains')
    titu_pac = django_filters.CharFilter(lookup_expr='icontains')
    pais_id = django_filters.NumberFilter()
    departamento_id = django_filters.NumberFilter()
    provincia_id = django_filters.NumberFilter()
    distrito_id = django_filters.NumberFilter()
    observacion = django_filters.CharFilter(lookup_expr='icontains')
    detalleodontograma_pac = django_filters.CharFilter(lookup_expr='icontains')
    sexo = django_filters.ChoiceFilter(choices=Paciente.Sexo.choices)
    esta_pac = django_filters.ChoiceFilter(choices=Paciente.Estado.choices)
    estudios_pac = django_filters.ChoiceFilter(choices=Paciente.Estudios.choices)

    class Meta:
        model = Paciente
        fields = [
            'nomb_pac', 'apel_pac', 'edad_pac', 'ocupacion', 'lugar_nacimiento',
            'informacion_clinica', 'dire_pac', 'telf_pac', 'dni_pac', 'fena_pac',
            'fecha_registro', 'civi_pac', 'afil_pac', 'aler_pac', 'emai_pac',
            'titu_pac', 'pais_id', 'departamento_id', 'provincia_id', 'distrito_id',
            'observacion', 'estudios_pac', 'detalleodontograma_pac', 'sexo', 'esta_pac'
        ]


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