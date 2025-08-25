from pathlib import Path
import os
import environ
import requests
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

TELEGRAM_TOKEN = env('telegram_token')
TELEGRAM_CHAT_ID = env('telegram_chat_id')

# Set the project base directory



class TelegramApiManager():
    def telegram_notify(self, text: str):
        if not (TELEGRAM_TOKEN and TELEGRAM_CHAT_ID):
            return
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
                timeout=10,
            )
        except Exception:
            # Don't crash the task because Telegram failed
            pass