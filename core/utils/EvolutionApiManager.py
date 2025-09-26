import requests


import time
import logging
import base64
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from pathlib import Path
import os
import environ
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)


# Set the project base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = os.path.join(BASE_DIR, '.env')
# Take environment variables from .env file
if os.path.exists(env_file):
    environ.Env.read_env(env_file)


evo_key = env('evo_key')
debug = env.bool('true_msg', default=False) 
logger = logging.getLogger(__name__)

class EvolutionApiManager:
    instance = env('evo_instance')
    key = evo_key
    base_url = env('evol_api_url')  # considerar cargar desde .env
    headers = {"Content-Type": "application/json", "apikey": key}

    def __init__(self, instance: str = None, key: str = None, base_url: str = None):
        if instance:
            self.instance = instance
        if key:
            self.key = key
        if base_url:
            self.base_url = base_url


    def _validate_number(self, number: str) -> bool:
        """Validación mínima: debe ser solo dígitos y al menos 8-9 dígitos (ajusta según tus requisitos)."""
        if not number:
            return False
        s = str(number).strip()
        return s.isdigit() and len(s) >= 8

    def send_message(self, number: str, message: str, timeout: float = 10.0, max_retries: int = 3, message_instance=env('evo_instance')):
        """
        Envía un mensaje y gestiona errores.

        Retorna un dict con:
        {
            "ok": bool,
            "status_code": int | None,
            "response": parsed_json_or_text_or_None,
            "error": str | None
        }
        """
        url = f"{self.base_url.rstrip('/')}/message/sendText/{message_instance}"

        # Validación básica del número
        if not self._validate_number(number):
            err = f"Número inválido: {repr(number)}"
            logger.error(err)
            return {"ok": False, "status_code": None, "response": None, "error": err}
        
        if not debug:
            payload = {"number": '51967244227', "text": message}
        else:
            payload = {"number": f'51{number}', "text": message}
        

        backoff = 1.0
        attempt = 0
        last_exception = None

        while attempt < max_retries:
            attempt += 1
            try:
                logger.debug("Sending message attempt %d to %s (url=%s)", attempt, number, url)
                resp = requests.post(url, json=payload, headers=self.headers, timeout=timeout)

                # Raise for HTTP errors (will be caught below)
                try:
                    resp.raise_for_status()
                except HTTPError:
                    # Not raising immediately; we want to capture body for debugging
                    logger.warning("HTTP error for %s: %s - %s", number, resp.status_code, resp.text)

                # Try to parse JSON safely
                try:
                    data = resp.json()
                except ValueError:
                    data = resp.text  # fallback to text

                # Treat 2xx as success
                if 200 <= resp.status_code < 300:
                    logger.info("Mensaje enviado (o aceptado) para %s: status=%s", number, resp.status_code)
                    return {"ok": True, "status_code": resp.status_code, "response": data, "error": None}
                else:
                    # For server errors (5xx), we may retry; for client errors (4xx) don't retry
                    if 500 <= resp.status_code < 600:
                        logger.warning(
                            "Server error (attempt %d/%d) for %s: %s - %s",
                            attempt, max_retries, number, resp.status_code, resp.text
                        )
                        last_exception = RuntimeError(f"Server returned {resp.status_code}: {resp.text}")
                        # wait and retry
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    else:
                        # 4xx - client error, do not retry
                        logger.error("Client error for %s: %s - %s", number, resp.status_code, resp.text)
                        return {"ok": False, "status_code": resp.status_code, "response": data, "error": f"Client error: {resp.status_code}"}

            except Timeout as e:
                logger.warning("Timeout en petición a %s (attempt %d/%d): %s", number, attempt, max_retries, str(e))
                last_exception = e
                time.sleep(backoff)
                backoff *= 2
                continue
            except ConnectionError as e:
                logger.warning("Connection error a %s (attempt %d/%d): %s", number, attempt, max_retries, str(e))
                last_exception = e
                time.sleep(backoff)
                backoff *= 2
                continue
            except RequestException as e:
                # base class for other requests exceptions
                logger.exception("Request exception al enviar a %s: %s", number, str(e))
                last_exception = e
                break
            except Exception as e:
                # Unexpected exceptions
                logger.exception("Unexpected error al enviar a %s: %s", number, str(e))
                last_exception = e
                break

        # Si llegamos aquí, todo fallo
        err_msg = None
        if last_exception:
            err_msg = f"Última excepción: {type(last_exception).__name__}: {str(last_exception)}"
        else:
            err_msg = "No se logró enviar el mensaje tras varios intentos."

        logger.error("Fallo al enviar mensaje a %s: %s", number, err_msg)
        return {"ok": False, "status_code": None, "response": None, "error": err_msg}
    
    def check_instance_state(self, timeout: float = 5.0, max_retries: int = 3):
        """
        Check the connection state of the instance.
        Returns: {"ok": bool, "status_code": int|None, "result": {"state": str, ...} | None, "error": str|None}
        """
        url = f'{self.base_url}instance/connectionState/{self.instance}'
        attempt = 0
        backoff = 1.0
        last_exc = None

        while attempt < max_retries:
            attempt += 1
            try:
                logger.debug("Checking instance state (attempt %d) url=%s", attempt, url)
                resp = requests.get(url, headers=self.headers, timeout=timeout)
                try:
                    resp.raise_for_status()
                except HTTPError:
                    logger.warning("HTTP error checking instance state: %s - %s", resp.status_code, resp.text)

                # parse JSON if possible
                try:
                    data = resp.json()
                except ValueError:
                    data = {"raw": resp.text}

                # Extract a sensible state if present
                state = None
                if isinstance(data, dict):
                    # many evolution APIs wrap within 'instance' -> { 'state': 'connecting' }
                    if "instance" in data and isinstance(data["instance"], dict):
                        state = data["instance"].get("state")
                    # fallback: top-level 'state'
                    state = state or data.get("state")

                return {"ok": True, "status_code": resp.status_code, "result": {"state": state, "data": data}, "error": None}

            except (Timeout, ConnectionError) as e:
                last_exc = e
                logger.warning("Network error checking instance state (attempt %d/%d): %s", attempt, max_retries, str(e))
                time.sleep(backoff)
                backoff *= 2
                continue
            except RequestException as e:
                last_exc = e
                logger.exception("RequestException checking instance state: %s", str(e))
                break
            except Exception as e:
                last_exc = e
                logger.exception("Unexpected error checking instance state: %s", str(e))
                break

        err = f"Failed to get instance state. Last error: {type(last_exc).__name__}: {str(last_exc)}" if last_exc else "Failed to get instance state."
        logger.error(err)
        return {"ok": False, "status_code": None, "result": None, "error": err}



if __name__ == "__main__":
    manager = EvolutionApiManager()

    # 1️⃣ Send test message
    print("📨 Sending Message...")
    print(manager.send_message(number="51967244237", message="Mensaje de Prueba"))

    # 3️⃣ Check Instance State
    print("\n🔍 Checking Instance State...")
    print(manager.check_instance_state())