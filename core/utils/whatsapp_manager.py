import requests
import logging
import json
import os
import environ
from pathlib import Path

# --- Environment Setup ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_file):
    environ.Env.read_env(env_file)

env = environ.Env(DEBUG=(bool, False))

logger = logging.getLogger(__name__)

class WhatsAppManager:
    """
    Direct client for Meta's WhatsApp Cloud API.
    Bypasses Chatwoot for reliable template sending.
    """
    def __init__(self):
        # Load these from your settings.py
        self.token = env("META_WHATSAPP_TOKEN")
        self.phone_number_id = env("META_PHONE_NUMBER_ID")
        self.version = "v19.0" 
        self.base_url = f"https://graph.facebook.com/{self.version}/{self.phone_number_id}/messages"
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def send_template(self, to_number: str, template_name: str, language_code: str = "es", components: list = None):
        """
        Sends a template message directly via Meta API.
        
        :param to_number: Target phone number (e.g. "51999999999")
        :param template_name: The exact name in WhatsApp Manager
        :param language_code: "es", "es_PE", "en_US"
        :param components: List of component dicts (header, body, buttons)
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                },
                "components": components if components else []
            }
        }

        return self._send_request(payload)

    def send_text_message(self, to_number: str, text_body: str):
        """
        Sends a simple text message (only works if 24h window is open).
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text_body
            }
        }
        return self._send_request(payload)

    def _send_request(self, payload: dict):
        """
        Internal method to handle the request with detailed logging.
        """
        try:
            # DEBUG LOG: Print the exact JSON we are sending
            logger.info(f"📤 Meta API Request to {payload.get('to')}:")
            logger.debug(json.dumps(payload, indent=2))

            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=10)
            
            # Check for HTTP Errors
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Success: Message ID {data['messages'][0]['id']}")
            return {"ok": True, "data": data}

        except requests.exceptions.HTTPError as e:
            # Capture the detailed Meta error message
            error_resp = e.response.json()
            error_msg = error_resp.get('error', {}).get('message', str(e))
            error_code = error_resp.get('error', {}).get('code', 'Unknown')
            
            logger.error(f"❌ Meta API Error ({error_code}): {error_msg}")
            logger.error(f"Payload was: {json.dumps(payload)}")
            
            return {"ok": False, "error": error_msg, "code": error_code}
            
        except Exception as e:
            logger.error(f"❌ Network/Client Error: {str(e)}")
            return {"ok": False, "error": str(e)}

    # --- HELPER: Component Builder ---
    # Use this to easily build the 'components' list for templates
    @staticmethod
    def build_components(body_vars: list = None, header_vars: list = None, button_payload: str = None):
        """
        Helper to construct the Meta component structure.
        """
        components = []

        # 1. Header Parameters
        if header_vars:
            parameters = []
            for var in header_vars:
                # Detect if it's text or image (simple logic)
                if var.startswith('http'):
                    parameters.append({"type": "image", "image": {"link": var}})
                else:
                    parameters.append({"type": "text", "text": str(var)})
            
            components.append({"type": "header", "parameters": parameters})

        # 2. Body Parameters
        if body_vars:
            parameters = [{"type": "text", "text": str(var)} for var in body_vars]
            components.append({"type": "body", "parameters": parameters})

        # 3. Button Payload (Dynamic URL suffix)
        if button_payload:
            # Index 0 means the first button in the template
            components.append({
                "type": "button",
                "sub_type": "url",
                "index": 0, 
                "parameters": [{"type": "text", "text": str(button_payload)}]
            })

        return components