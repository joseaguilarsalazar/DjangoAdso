from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from core.models import Clinica,  Consultorio
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

User = get_user_model()

def parse_date(value):
    try:
        return make_aware(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
    except:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except:
            return None


def parse_value(value):
    if value in ("", "NULL", None):
        return None
    return value.strip()


class Command(BaseCommand):
    help = 'Importa pacientes y especialidades desde archivos CSV'

    def handle(self, *args, **kwargs):

        #crear Clinicas

        clinicaIquitos, created = Clinica.objects.get_or_create(
            nomb_clin='Clinica Dental Sede Iquitos',
            defaults={
                'direc_clin': 'Calle Callao 176',
                'telf_clin': 917435154,
                'email_clin': 'email 1',
            }
        )
        

        #create consultorios

        for i in range(2):
            consultorio, create = Consultorio.objects.get_or_create(
                nombreConsultorio = f'Iquitos n {i+1}',
                clinica = clinicaIquitos
            )


        
