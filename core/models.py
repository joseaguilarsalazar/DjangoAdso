from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Especialidad(models.Model):
    descripcion = models.CharField(max_length=200)
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
    tipo_doc    = models.CharField("Tipo de documento", max_length=50)
    num_doc     = models.CharField("Número de documento", max_length=50, unique=True)
    nombre      = models.CharField("Nombre completo", max_length=150)
    direccion   = models.CharField("Dirección", max_length=200, blank=True, null=True)
    telefono    = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    email       = models.EmailField("Correo electrónico", blank=True, null=True)
    fecha_nac   = models.DateField("Fecha de nacimiento", blank=True, null=True)
    sexo        = models.CharField("Sexo", max_length=10, choices=[
        ("M", "Masculino"),
        ("F", "Femenino"),
        ("O", "Otro"),
    ], blank=True, null=True)
    
    observaciones = models.TextField("Observaciones", blank=True, null=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.medico.medico:
            raise ValidationError(f"El usuario {self.medico} no está marcado como médico.")

    def __str__(self):
        return f"{self.nombre} ({self.num_doc})"
    

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

    tratamiento = models.ForeignKey('Tratamiento', on_delete=models.SET_NULL, null=True)
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
    
class Pagos(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.SET_NULL, null=True)
    monto = models.FloatField()
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.paciente.__str__} : {self.created_at}'