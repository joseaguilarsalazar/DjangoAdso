import django_filters
from .models import (
    Tratamiento, 
    Especialidad, 
    Cita, 
    Paciente,
    Clinica,
    Alergia,
    PacienteAlergia,
    Banco,
    Categoria,
    Enfermedad,
    PacienteEvolucion,
    PacienteEnfermedad,
    PacienteDiagnostico,
    PacientePlaca,
    )

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


class TratamientoFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()  # ?created_at_after=YYYY-MM-DD&created_at_before=YYYY-MM-DD
    asunto = django_filters.CharFilter(lookup_expr='icontains')  # partial match search
    observacion = django_filters.CharFilter(lookup_expr='icontains', required=False)  # partial match search

    class Meta:
        model = Tratamiento
        fields = {
            'paciente': ['exact'],  # filter by patient ID
            'medico': ['exact'],    # filter by doctor ID
            'asunto': ['exact'],    # exact match (icontains already covers partial)
            'created_at': ['exact', 'date__gte', 'date__lte'],
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
            'medico': ['exact'],
            'paciente': ['exact'],
            'fecha': ['gte', 'lte'],
            'estadoCita': ['exact'],
            'estadoPago': ['exact'],
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

class PacienteDiagnosticoFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()  # allows filtering between dates (created_at_after, created_at_before)

    class Meta:
        model = PacienteDiagnostico
        fields = {
            'paciente': ['exact'],      # filter by paciente ID
            'enfermedad': ['exact'],    # filter by enfermedad ID
            'activo': ['exact'],        # filter by active status (True/False)
            'created_at': ['exact', 'date__gte', 'date__lte'],
        }

class PacientePlacaFilter(django_filters.FilterSet):
    # Optional: allows date range filtering with ?created_at_after=YYYY-MM-DD&created_at_before=YYYY-MM-DD
    created_at = django_filters.DateFromToRangeFilter()
    
    # Optional: search by nombre (case-insensitive partial match)
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = PacientePlaca
        fields = {
            'paciente': ['exact'],    # filter by patient ID
            'activo': ['exact'],      # true/false
            'nombre': ['exact'],      # exact match (we also added icontains above)
            'created_at': ['exact', 'date__gte', 'date__lte'],
        }