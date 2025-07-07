from rest_framework import views
from ..models import Paciente
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import requests
from djangoAdso.settings import evo_key
from rest_framework import status
import time
import logging
from random import randint

logger = logging.getLogger(__name__)

class EnvioMensajeAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        api_url = 'https://evol-evolution-api.jmtqu4.easypanel.host/message/sendText/test_instance'
        api_key = evo_key  # Idealmente usar settings o variable de entorno
        enviados = 0
        errores = []

        pacientes = Paciente.objects.exclude(telf_pac__isnull=True).exclude(telf_pac__exact='')
        already_sent = []

        for paciente in pacientes:
            numero = f"51{paciente.telf_pac.strip()}"
            mensaje = f'Buenas tardes {paciente.nomb_pac}, le saludamos del centro odontológico ADSO estamos revisando nuestra base de datos y nos figura su contacto como paciente, para saber cómo le fue en su último tratamiento , quisieramos agendar una cita de evaluación más fluorizacion sin costo como manera preventiva. Le gustaría agendar una cita ? Me indica sus datos completos por favor 🦷🤝'

            if numero not in already_sent:
                already_sent.append(numero)
                try:
                    response = requests.post(
                        api_url,
                        json={"number": numero, "text": mensaje},
                        headers={
                            "Content-Type": "application/json",
                            "apikey": api_key
                        },
                        timeout=10  # previene que se quede colgado
                    )

                    if response.status_code == 200:
                        enviados += 1
                    else:
                        logger.warning(f"Error para {numero}: {response.status_code} - {response.text}")
                        errores.append(numero)

                    time.sleep(float(randint(15, 25)))  # prevenir rate-limit
                except Exception as e:
                    logger.error(f"Excepción para {numero}: {str(e)}")
                    errores.append(numero)

        return Response({
            'enviados': enviados,
            'errores': errores,
            'total': pacientes.count()
        }, status=status.HTTP_200_OK)

