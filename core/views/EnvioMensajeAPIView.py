from rest_framework import views
from ..models import Paciente
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import requests
from djangoAdso.settings import evo_key
from rest_framework import status
import time
import logging
import traceback
from random import randint

logger = logging.getLogger(__name__)

class EnvioMensajeAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        api_url = 'https://evolution-api-evolution-api.4oghcf.easypanel.host/message/sendText/adso_iquitos_instance'
        api_key = evo_key  # Idealmente usar settings o variable de entorno
        enviados = 0
        errores = []

        pacientes = [
    '990643439',
    '986428906',
    '940421575',
    '94858940',
    '960197917',
    '944826970',
    '929450814',
    '913950205',
    '958697273',
    '945285413',
    '963368770',
    '965644590',
    '978001619',
    '921927051',
    '931563375'
]
        already_sent = []
        response = requests.post(
                        api_url,
                        json={"number": '51967244227', "text": 'Message send started'},
                        headers={
                            "Content-Type": "application/json",
                            "apikey": api_key
                        },
                        timeout=10  # previene que se quede colgado
                    )


        for paciente in pacientes:
            numero = f"51{str(paciente)}"
            mensaje = f"""Hola 👋, le saludamos del Centro Odontológico ADSO.
Ah pasado un tiempo desde su última visita con nosotros, nos gustaría saber si desea agendar una cita para una evaluación dental sin costo alguno como parte de su convenio. 
Quedamos atentos a su confirmación y esperamos su pronta respuesta.
Muchas gracias que tenga un excelente y bendecido día😊"""

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
                        logger.warning(
                            f"Error para {numero}: "
                            f"{response.status_code} - {response.text} | "
                            f"Request Data: { {'number': numero, 'text': mensaje} }"
                        )
                        errores.append(numero)

                    time.sleep(float(randint(15, 25)))  # prevenir rate-limit

                except Exception as e:
                    logger.error(
                        f"Excepción para {numero}: {type(e).__name__} - {str(e)}\n"
                        f"Traceback:\n{traceback.format_exc()}"
                    )
                    errores.append(numero)

        return Response({
            'enviados': enviados,
            'errores': errores,
            'total': pacientes.count()
        }, status=status.HTTP_200_OK)

