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
import csv

logger = logging.getLogger(__name__)

from pathlib import Path
import os
import environ

env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_file):
    environ.Env.read_env(env_file)

evo_path = env('evol_api_url')

# new: path to the CSV (same folder as this view file)
CSV_PATH = Path(__file__).resolve().parent / 'cell_phones.csv'

def _load_phone_numbers(csv_path: Path):
	"""
	Load phone numbers from CSV and normalize according to rules:
	- remove non-digit characters
	- ignore if length < 8 or > 10
	- if length == 8, prepend '9'
	- keep length 9 or 10 as-is
	Returns a list of unique numeric strings (order preserved).
	"""
	if not csv_path.exists():
		logger.warning("CSV not found: %s", csv_path)
		return []

	numbers = []
	try:
		with csv_path.open(newline='', encoding='utf-8') as fh:
			reader = csv.DictReader(fh)
			for row in reader:
				raw = (row.get('cell') or '').strip()
				if not raw:
					continue
				# keep digits only
				digits = ''.join(ch for ch in raw if ch.isdigit())
				if not digits:
					continue
				l = len(digits)
				# apply rules
				if l < 8 or l > 10:
					continue
				if l == 8:
					digits = '9' + digits
				# accept 9 or 10 as-is
				numbers.append(digits)
	except Exception as e:
		logger.error("Error reading CSV %s: %s", csv_path, e)
		return []

	# dedupe preserving order
	seen = set()
	unique = []
	for n in numbers:
		if n not in seen:
			seen.add(n)
			unique.append(n)
	return unique

class EnvioMensajeAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # simple test password protection
        password = request.data.get('password')
        if password != 'secret_password':
            return Response({'detail': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

        api_url = f'{evo_path}message/sendText/adso_instance'
        api_key = evo_key  # Idealmente usar settings o variable de entorno
        enviados = 0
        errores = []

        pacientes = _load_phone_numbers(CSV_PATH)
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
            mensaje = f"""¡¡Buen día estimado paciente de la Institución : Jardín N 26 !! Le saludamos de la clínica odontológica Adso dent sede Yurimaguas para coordinar la cita odontológica que consta en una evaluación y aplicación de flúor sin costo por convenio con la Institución Educativa. ¿Qué día y en qué horario le agendamos?.. esparemos su pronta respuesta, cualquier urgencia dental estamos para atudarlo .
Que tengan un bendecido día🤗
"""

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
            'total': len(pacientes)
        }, status=status.HTTP_200_OK)

