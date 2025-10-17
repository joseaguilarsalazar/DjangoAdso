from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Especialidad(models.Model):
    nombre = models.CharField(max_length=200, null=True)
    honorariosPorcentaje = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], default=0.3)
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
    photo = models.CharField("Foto (ruta)", max_length=300, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nomb_clin

class User(AbstractUser):
    objects = UserManager()

    username = None  # Eliminamos el username tradicional

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    old_cod_med = models.IntegerField(null=True, blank=True) #this field is to store the old id of the previous db

    email       = models.EmailField(_('email address'), unique=True)
    tipo_doc    = models.CharField("Tipo de documento", max_length=50)
    num_doc     = models.CharField("Número de documento", max_length=50, unique=True)
    name        = models.CharField("Nombre completo", max_length=150)
    direccion   = models.CharField("Dirección", max_length=200)
    telefono    = models.CharField("Teléfono", max_length=20, null=True, blank=True)
    foto        = models.ImageField("Foto de perfil", upload_to='user_photos/', null=True, blank=True)

    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)
    is_especialista = models.BooleanField("¿Es especialista?", default=False)
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
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
        return f"{self.name} {self.last_name}"
    

class Paciente(models.Model):
    old_cod_pac = models.IntegerField(null=True, blank=True)
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
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    
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
        return f"{self.nomb_pac} {self.apel_pac}"
    
class Alergia(models.Model):
    nombre_ale = models.CharField("Nombre de la alergia", max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_ale or f"Alergia #{self.cod_ale}"

class PacienteAlergia(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    alergia = models.ForeignKey(Alergia, on_delete=models.CASCADE)
    observacion = models.TextField(max_length=200, null=True, blank=True)

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

    
class Categoria(models.Model):
    nomb_cat = models.CharField("Nombre de la categoría", max_length=45, blank=True, null=True)
    esta_cat = models.CharField("Estado", max_length=1, blank=True, null=True)

    def __str__(self):
        return self.nomb_cat or f"Categoría #{self.codi_cat}"

class CategoriaTratamiento(models.Model):
    nombre = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tratamiento(models.Model):
    nombre = models.CharField(max_length=2000)
    precioBase = models.FloatField()
    precioConvenio = models.FloatField(null=True, blank=True)
    categoria = models.ForeignKey(CategoriaTratamiento, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre


class TratamientoPaciente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    convenio = models.BooleanField(default=False)

    asunto = models.CharField(max_length=200, default='tratamiento')
    observacion = models.TextField(max_length=1000, null=True, blank=True)

    descuento = models.FloatField()
    descuento_porcentaje = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.asunto


    
class Consultorio(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    nombreConsultorio = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.nombreConsultorio if self.nombreConsultorio else self.id
    


class Cita(models.Model):
    old_cod_cit = models.IntegerField(null=True, blank=True)
    medico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True)
    consultorio = models.ForeignKey(Consultorio, on_delete=models.CASCADE, null=True, blank=True)

    cancelado = models.BooleanField(default=False)
    reprogramado = models.BooleanField(default=False)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.SET_NULL, null=True, blank=True)

    fecha = models.DateField()
    hora = models.TimeField()

    reminder_sent = models.BooleanField(default=False, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cita {self.paciente.name} {self.paciente.last_name} {self.fecha}"
    

class Enfermedad(models.Model):
    codigo = models.CharField(max_length=20, null=True, blank=True)
    descripcion = models.CharField("Descripción", max_length=200, blank=True, null=True)
    estado = models.CharField("Estado", max_length=1, default='S')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.descripcion or f"Enfermedad {self.id}"
    
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

class PacienteDiagnostico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    enfermedad = models.ForeignKey(Enfermedad, on_delete=models.CASCADE)

    activo = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PacientePlaca(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)

    notas = models.TextField(max_length=1000, null=True, blank=True)
    archivo = models.ImageField(null=True)

    activo = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    
