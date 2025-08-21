# create_superuser.py
import os
import django
from core.models import Clinica

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoAdso.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

clinicaIquitos, created = Clinica.objects.get_or_create(
            nomb_clin='Clinica Dental Sede Iquitos',
            defaults={
                'direc_clin': 'Calle Callao 176',
                'telf_clin': 917435154,
                'email_clin': 'email 1',
            }
        )

if not User.objects.filter(email='admin@gmail.com').exists():
    User.objects.create_superuser(
        email='admin@gmail.com',
        password='1234',
        tipo_doc='DNI',
        num_doc='00000001',
        name='Administrador General',
        rol='admin',
        estado='activo',
        clinica = clinicaIquitos,
    )

