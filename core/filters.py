import django_filters
import django_filters as filters
from django.db.models import Sum, F, FloatField, Q
from django.db.models.functions import Coalesce
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
    Consultorio,
    CategoriaTratamiento,
    TratamientoPaciente,
    )
from django.contrib.auth import get_user_model
from django.db.models.functions import TruncDate

User = get_user_model()

class UserFilter(django_filters.FilterSet):
    # text searches
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    direccion = django_filters.CharFilter(field_name="direccion", lookup_expr="icontains")
    telefono = django_filters.CharFilter(field_name="telefono", lookup_expr="icontains")
    num_doc = django_filters.CharFilter(field_name="num_doc", lookup_expr="icontains")
    tipo_doc = django_filters.CharFilter(field_name="tipo_doc", lookup_expr="iexact")

    # exact choices
    rol = django_filters.CharFilter(field_name="rol", lookup_expr="iexact")
    estado = django_filters.CharFilter(field_name="estado", lookup_expr="iexact")

    # foreign key (by id) and by name
    especialidad = django_filters.NumberFilter(field_name="especialidad__id", lookup_expr="exact")
    especialidad_nombre = django_filters.CharFilter(field_name="especialidad__nombre", lookup_expr="icontains")

    # date range on created_at
    created_at_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = User
        fields = [
            "name", "email", "direccion", "telefono", "num_doc", "tipo_doc",
            "rol", "estado", "especialidad", "especialidad_nombre",
            "created_at_after", "created_at_before",
        ]

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

    has_debt = django_filters.BooleanFilter(method='filter_has_debt')

    class Meta:
        model = Paciente
        fields = [
            'nomb_pac', 'apel_pac', 'edad_pac', 'ocupacion', 'lugar_nacimiento',
            'informacion_clinica', 'dire_pac', 'telf_pac', 'dni_pac', 'fena_pac',
            'fecha_registro', 'civi_pac', 'afil_pac', 'aler_pac', 'emai_pac',
            'titu_pac', 'pais_id', 'departamento_id', 'provincia_id', 'distrito_id',
            'observacion', 'estudios_pac', 'detalleodontograma_pac', 'sexo', 'esta_pac'
        ]

    def filter_has_debt(self, queryset, name, value):
        """
        value=True  -> pacientes con deuda
        value=False -> todos los pacientes
        """
        # Anotar el total pagado y el total de tratamientos
        queryset = queryset.annotate(
            total_pagado=Coalesce(Sum('tratamientopaciente__ingresos__monto'), 0.0, output_field=FloatField()),
            total_tratamiento=Coalesce(Sum('tratamientopaciente__tratamiento__precioBase'), 0.0, output_field=FloatField())
        )

        if value:
            # Solo los pacientes con deuda
            return queryset.filter(total_pagado__lt=F('total_tratamiento'))
        else:
            return queryset

class TratamientoFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()  # ?created_at_after=YYYY-MM-DD&created_at_before=YYYY-MM-DD

    class Meta:
        model = Tratamiento
        fields = {
            'created_at': ['exact', 'date__gte', 'date__lte'],
        }

class EspecialidadFilter(django_filters.FilterSet):
    class Meta:
        model = Especialidad
        fields = {
            'descripcion': ['icontains'],
        }


import django_filters as filters
from .models import Cita, User, Paciente, Consultorio

class CitaFilter(filters.FilterSet):
    # FK filters (by id, convenient for frontends)
    medico_id = filters.NumberFilter(field_name='medico__id')
    paciente_id = filters.NumberFilter(field_name='paciente__id')
    consultorio_id = filters.NumberFilter(field_name='consultorio__id')

    # Permite traer registros sin consultorio
    consultorio_isnull = filters.BooleanFilter(field_name='consultorio', lookup_expr='isnull')

    # Booleans
    cancelado = filters.BooleanFilter()
    reprogramado = filters.BooleanFilter()
    reminder_sent = filters.BooleanFilter()

    # Fecha exacta y rango
    fecha = filters.DateFilter(field_name='fecha')  # ?fecha=YYYY-MM-DD
    fecha_after = filters.DateFilter(field_name='fecha', lookup_expr='gte')  # ?fecha_after=YYYY-MM-DD
    fecha_before = filters.DateFilter(field_name='fecha', lookup_expr='lte')  # ?fecha_before=YYYY-MM-DD

    # Límites de hora
    hora_after = filters.TimeFilter(field_name='hora', lookup_expr='gte')   # ?hora_after=07:00
    hora_before = filters.TimeFilter(field_name='hora', lookup_expr='lte')  # ?hora_before=12:00

    # Rango por created_at
    created_at_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')


    tratamiento_id = filters.NumberFilter(field_name='tratamiento__id')

    class Meta:
        model = Cita
        fields = [
            # by id
            'medico_id', 'paciente_id', 'consultorio_id',
            # null check
            'consultorio_isnull',
            # flags
            'cancelado', 'reprogramado', 'reminder_sent',
            # fecha & hora
            'fecha', 'fecha_after', 'fecha_before', 'hora_after', 'hora_before',
            # created_at
            'created_at_after', 'created_at_before',
            # tratamiento_id
            'tratamiento_id',
        ]



class EnfermedadFilter(django_filters.FilterSet):
    codigo = django_filters.CharFilter(lookup_expr='icontains')
    descripcion = django_filters.CharFilter(lookup_expr='icontains')
    estado = django_filters.CharFilter()

    class Meta:
        model = Enfermedad
        fields = ['codigo','descripcion', 'estado']


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

class ConsultorioFilter(django_filters.FilterSet):
    class Meta:
       model = Consultorio
       fields = {
           'clinica': ['exact'],
       }

class CategoriaTratamientoFilter(django_filters.FilterSet):
    class Meta:
        model = CategoriaTratamiento
        fields = {
            'nombre' : ['icontains']
        }

class TratamientoFilter(django_filters.FilterSet):
    categoria_id = django_filters.NumberFilter(
        field_name='categoria_id',
        lookup_expr='exact'
    )
    class Meta:
        model: Tratamiento
        fields = [
            'categoria_id'
        ]

class TratamientoPacienteFilter(django_filters.FilterSet):
    paciente = django_filters.NumberFilter(
        field_name='paciente_id',
        lookup_expr='exact'
    )
    tratamiento = django_filters.NumberFilter(
        field_name='tratamiento_id',
        lookup_expr='exact'
    )

    # New text filters
    paciente_nombre = django_filters.CharFilter(method='filter_paciente_nombre')
    tratamiento_nombre = django_filters.CharFilter(field_name='tratamiento__nombre', lookup_expr='icontains')

    descuento_min = django_filters.NumberFilter(field_name='descuento', lookup_expr='gte')
    descuento_max = django_filters.NumberFilter(field_name='descuento', lookup_expr='lte')

    created_date_after = django_filters.DateFilter(method='filter_created_after')
    created_date_before = django_filters.DateFilter(method='filter_created_before')

    class Meta:
        model = TratamientoPaciente
        fields = [
            'paciente',
            'tratamiento',
            'paciente_nombre',
            'tratamiento_nombre',
            'descuento_min',
            'descuento_max',
            'created_date_after',
            'created_date_before',
        ]

    def filter_created_after(self, queryset, name, value):
        return queryset.annotate(cdate=TruncDate('created_at')).filter(cdate__gte=value)

    def filter_created_before(self, queryset, name, value):
        return queryset.annotate(cdate=TruncDate('created_at')).filter(cdate__lte=value)

    def filter_paciente_nombre(self, queryset, name, value):
        return queryset.filter(
            Q(paciente__nomb_pac__icontains=value) |
            Q(paciente__apel_pac__icontains=value)
        )