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
        api_url = 'https://evolution-api-evolution-api.4oghcf.easypanel.host/message/sendText/adso_instance'
        api_key = evo_key  # Idealmente usar settings o variable de entorno
        enviados = 0
        errores = []

        pacientes = Paciente.objects.exclude(telf_pac__isnull=True).exclude(telf_pac__exact='').filter(departamento_id=1)
        already_sent = []

        for paciente in pacientes:
            numero = f"51{paciente.telf_pac.strip()}"
            mensaje = f"""Buenos días Estimados Pacientes en esta oportunidad con mucho agrado estamos comunicando que nuestro Equipo de Trabajo (Clínica Odontológica Especializada ADSO) en este mes de Julio está brindando un beneficio en los Tratamientos de Odontología Estética y Ortodoncia 🦷por ser nuestro mes Patrio.🇵🇪 

SI REQUIERE MAYOR INFORMACIÓN NUESTRA ASISTENTE DE ENFERMERÍA ESTARÁ GUSTOSA DE AYUDARLOS PARA MAYOR INFORMACIÓN Y/O CITAS EN NUESTRA NUEVA SEDE EN LA CIUDAD DE YURIMAGUAS 

Que pase un feliz fin de semana y Bendiciones para usted y su familia 😊"""

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

