# create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoAdso.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()


if not User.objects.filter(email='admin@gmail.com').exists():
    User.objects.create_superuser(
        email='admin@gmail.com',
        password='1234',
        tipo_doc='DNI',
        num_doc='00000001',
        name='Administrador General',
        rol='admin',
        estado='activo',
        clinica_id = 1,
    )

