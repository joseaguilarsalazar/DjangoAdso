from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Especialidad(models.Model):
    nombre = models.CharField(max_length=200, null=True)
    honorariosPorcentaje = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    descripcion = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.descripcion


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Clinica(models.Model):
    nomb_clin = models.CharField("Nombre de la clínica", max_length=100)
    direc_clin = models.CharField("Dirección", max_length=100)
    telf_clin = models.BigIntegerField("Teléfono")  # int(11) puede exceder IntegerField
    email_clin = models.EmailField("Correo electrónico", max_length=100)
    ruc_clin = models.CharField("RUC", max_length=15, blank=True, null=True)
    fecha_clin = models.DateField("Fecha", blank=True, null=True)
    photo = models.CharField("Foto (ruta)", max_length=300, blank=True, null=True)
    cod_plan = models.IntegerField("Código de plan")
    esta_clin = models.CharField("Estado", max_length=1, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nomb_clin

class User(AbstractUser):
    objects = UserManager()

    username = None  # Eliminamos el username tradicional

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email       = models.EmailField(_('email address'), unique=True)
    tipo_doc    = models.CharField("Tipo de documento", max_length=50)
    num_doc     = models.CharField("Número de documento", max_length=50, unique=True)
    name        = models.CharField("Nombre completo", max_length=150)
    direccion   = models.CharField("Dirección", max_length=200)
    telefono    = models.CharField("Teléfono", max_length=20, null=True, blank=True)
    foto        = models.ImageField("Foto de perfil", upload_to='user_photos/', null=True, blank=True)

    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True)

    estado      = models.CharField("Estado", max_length=50)
    ROL_CHOICES = [
        ('medico', 'Médico'),
        ('admin', 'Administrador'),
        ('enfermero', 'Enfermero/a'),
    ]

    rol = models.CharField("Rol", max_length=50, choices=ROL_CHOICES)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
    

class Paciente(models.Model):
    nomb_pac              = models.CharField("Nombres", max_length=20,blank=True, null=True)
    apel_pac              = models.CharField("Apellidos", max_length=20, blank=True, null=True)
    edad_pac              = models.CharField("Edad", max_length=3,blank=True, null=True)
    ocupacion             = models.CharField("Ocupación", max_length=40, blank=True, null=True)
    lugar_nacimiento      = models.CharField("Lugar de nacimiento", max_length=30, blank=True, null=True)
    informacion_clinica   = models.CharField("Información clínica", max_length=70, blank=True, null=True)
    dire_pac              = models.CharField("Dirección", max_length=100, blank=True, null=True)
    telf_pac              = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    dni_pac               = models.CharField("DNI", max_length=10, unique=True, blank=True, null=True)
    foto_paciente         = models.CharField("Foto (ruta)", max_length=255, blank=True, null=True)
    fena_pac              = models.DateField("Fecha de nacimiento", blank=True, null=True)
    fecha_registro        = models.DateTimeField("Fecha de registro", auto_now_add=True, blank=True, null=True)
    civi_pac              = models.CharField("Estado civil", max_length=1, blank=True, null=True)
    afil_pac              = models.CharField("Afiliación", max_length=30, blank=True, null=True)
    aler_pac              = models.CharField("Alergias", max_length=120, blank=True, null=True)
    emai_pac              = models.EmailField("Correo electrónico", max_length=50, blank=True, null=True)
    titu_pac              = models.CharField("Titular", max_length=20, blank=True, null=True)
    pais_id               = models.IntegerField("ID país", blank=True, null=True)
    departamento_id       = models.IntegerField("ID departamento", blank=True, null=True)
    provincia_id          = models.IntegerField("ID provincia", blank=True, null=True)
    distrito_id           = models.IntegerField("ID distrito", blank=True, null=True)
    observacion           = models.CharField("Observaciones", max_length=100, blank=True, null=True)
    
    registro_pac          = models.DateTimeField("Registro paciente", auto_now_add=True, blank=True, null=True)
    
    detalleodontograma_pac = models.TextField("Detalle Odontograma", blank=True, null=True)

    class Sexo(models.TextChoices):
        MASCULINO = 'MASCULINO', 'Masculino'
        FEMENINO = 'FEMENINO', 'Femenino'

    sexo = models.CharField(max_length=100, choices=Sexo, default=Sexo.MASCULINO)

    class Estado(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        INACTIVO = 'INACTIVO', 'Inactivo'

    esta_pac              = models.CharField("Estado", max_length=8, choices=Estado, default=Estado.ACTIVO)

    class Estudios(models.TextChoices):
        NINGUNO = 'NINGUNO', 'Ninguno'
        PRIMARIA = 'PRIMARIA', 'Primaria'
        SECUNDARIA = 'SECUNDARIA', 'Secundaria'
        TECNICO = 'TECNICO', 'Tecnico'
        UNIVERSITARIO = 'UNIVERSITARIO', 'Universitario'

    estudios_pac          = models.CharField("Estudios", max_length=100, choices=Estudios, default=Estudios.SECUNDARIA)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nomb_pac} {self.apel_pac} ({self.dni_pac})"
    
class Alergia(models.Model):
    nombre_ale = models.CharField("Nombre de la alergia", max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_ale or f"Alergia #{self.cod_ale}"

class PacienteAlergia(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    alergia = models.ForeignKey(Alergia, on_delete=models.CASCADE)
    observacion = models.TextField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Banco(models.Model):
    descripcion = models.CharField("Descripción", max_length=80, blank=True, null=True)
    
    ESTADO_CHOICES = [
        (1, "Activo"),
        (2, "Inactivo"),
    ]
    estado = models.IntegerField("Estado", choices=ESTADO_CHOICES, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.descripcion or f"Banco #{self.cod_banco}"
    
class Historial(models.Model):
    id_paciente   = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        db_column='id_paciente',
        related_name='historiales'
    )
    trata_medic   = models.BooleanField(default=False)
    propen_hemo   = models.BooleanField(default=False)
    alergico      = models.BooleanField(default=False)
    hipertenso    = models.BooleanField(default=False)
    diabetico     = models.BooleanField(default=False)
    embarazada    = models.BooleanField(default=False)
    motivo_consul = models.TextField()
    diagnostico   = models.TextField()
    observacion   = models.TextField(blank=True, null=True)
    referido      = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'historial'
        verbose_name = 'Historial'
        verbose_name_plural = 'Historiales'

    def __str__(self):
        return f"Historial de {self.id_paciente.name}"
    
class Categoria(models.Model):
    nomb_cat = models.CharField("Nombre de la categoría", max_length=45, blank=True, null=True)
    esta_cat = models.CharField("Estado", max_length=1, blank=True, null=True)

    def __str__(self):
        return self.nomb_cat or f"Categoría #{self.codi_cat}"

class Tratamiento(models.Model):
    tratamiento = models.CharField(max_length=200)
    precio = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tratamiento
    
class Cita(models.Model):
    class EstadoCita(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        COMPLETADA = 'COMPLETADA', 'Completada'

    class EstadoPago(models.TextChoices):
        NO_PAGADO = 'NO_PAGADO', 'No Pagado'
        PARCIAL = 'PARCIAL', 'Parcial'
        PAGADO = 'PAGADO', 'Pagado'

    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.SET_NULL, null=True)
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    hora = models.TimeField()
    enfermedad = models.CharField(max_length=100)

    estadoCita = models.CharField(max_length=15, choices=EstadoCita.choices, default=EstadoCita.PENDIENTE)
    estadoPago = models.CharField(max_length=15, choices=EstadoPago.choices, default=EstadoPago.NO_PAGADO)

    costo = models.FloatField()
    pagado = models.FloatField()
    saldo = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cita {self.paciente.name} {self.paciente.last_name} {self.fecha}"
    

class Enfermedad(models.Model):
    descripcion = models.CharField("Descripción", max_length=200, blank=True, null=True)
    estado = models.CharField("Estado", max_length=1, default='S')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.desc_enf or f"Enfermedad {self.codi_enf}"
    
class PacienteEvolucion(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True)
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.paciente.__str__} {self.created_at}'
    
class PacienteEnfermedad(models.Model):
    enfermedad = models.ForeignKey(Enfermedad, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)