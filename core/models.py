from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager

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

    username = None  # remove the username field

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField('email address', unique=True)

    tipo_doc    = models.CharField("tipo_de_documento", max_length=50)
    num_doc     = models.CharField("numero_de_documento", max_length=50, unique= True) #put unique later
    name        = models.CharField("nombre_completo", max_length=150)
    rol         = models.CharField("rol", max_length=50)
    estado      = models.CharField("estado", max_length=50)
    foto        = models.ImageField("foto_de_perfil", upload_to='user_photos/', null=True, blank=True)
    telefono    = models.CharField("Teléfono", max_length=20, null=True, blank=True)
    id_medico   = models.PositiveIntegerField("id_medico", null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
    

class PacienteManager(models.Manager):
    def buscar(self, dato):
        """
        Equivalente a scopeBuscar de Laravel:
        busca en num_doc o en name haciendo un __icontains.
        """
        return super().get_queryset().filter(
            Q(num_doc__icontains=dato) |
            Q(name__icontains=dato)
        )

class Paciente(User):
    """
    Proxy model sobre User para tratar específicamente a los pacientes.
    No crea tabla nueva; reutiliza 'users'.
    """
    objects = PacienteManager()

    class Meta:
        proxy = True
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return f"{self.name}"
    

class Historial(models.Model):
    id_paciente   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
    
class Especialidad(models.Model):
    descripcion = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.descripcion
    
class Medico(models.Model):
    nombres = models.CharField(max_length=200)
    apellidos = models.CharField(max_length=200)
    DNI= models.CharField(max_length=8)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True)
    direccion = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

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
    medico = models.ForeignKey('Medico', on_delete=models.SET_NULL, null=True)
    paciente = models.ForeignKey('Paciente', on_delete=models.SET_NULL, null=True)
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