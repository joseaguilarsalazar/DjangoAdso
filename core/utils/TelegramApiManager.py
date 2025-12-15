import os
import logging
import requests
import environ
from pathlib import Path

# Setup simple logging (you can configure this in your main settings.py instead)
logger = logging.getLogger(__name__)

# Initialize Environment
env = environ.Env(DEBUG=(bool, False))
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# Load Token globally (or you can move this into __init__)
TELEGRAM_TOKEN = env('telegram_token', default=None)

class TelegramApiManager:
    def __init__(self, token: str = None):
        # Allow passing token manually, or fallback to env
        self.token = token or TELEGRAM_TOKEN
        if not self.token:
            logger.warning("Telegram Token is missing. Notifications will not be sent.")

    def telegram_notify(self, chat_id: str | int, text: str) -> bool:
        """
        Sends a message to a specific Telegram chat.
        Returns True if successful, False otherwise.
        """
        if not self.token:
            logger.error("Attempted to send Telegram message without a configured Bot Token.")
            return False

        if not chat_id or not text:
            logger.warning("Missing 'chat_id' or 'text'. Skipping Telegram notification.")
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": text,
            "parse_mode": "HTML" # Optional: Allows you to use bold/italics
        }

        try:
            response = requests.post(url, json=payload, timeout=5)
            response_data = response.json()

            # Check for HTTP errors (4xx, 5xx)
            response.raise_for_status()

            # Check for Telegram API logical errors (e.g., bot kicked from group)
            if not response_data.get("ok"):
                error_msg = response_data.get("description", "Unknown Error")
                logger.error(f"Telegram API Error: {error_msg} (Chat ID: {chat_id})")
                return False

            logger.info(f"Telegram message sent successfully to {chat_id}")
            return True

        except requests.exceptions.Timeout:
            logger.error(f"Telegram request timed out for chat {chat_id}")
        except requests.exceptions.ConnectionError:
            logger.error("Connection error while contacting Telegram API")
        except requests.exceptions.HTTPError as e:
            # This catches 400/500 errors
            logger.error(f"HTTP Error sending Telegram message: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in telegram_notify: {e}")

        return False