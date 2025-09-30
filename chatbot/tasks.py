from celery import shared_task
from django.conf import settings
from chatbot.orchestrator.orchestrator import Orchestrator
from chatbot.models import Chat, Message
from core.utils.EvolutionApiManager import EvolutionApiManager
import redis
from pathlib import Path
import os
import environ
from djangoAdso.settings import REDIS_URL

manager = EvolutionApiManager()

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = os.path.join(BASE_DIR, '.env')


if os.path.exists(env_file):
    environ.Env.read_env(env_file)

r = redis.Redis.from_url(REDIS_URL)

debug = env.bool('true_msg', default=False) 

@shared_task
def process_user_buffer(sender: str):
    print('a')
    key = f"chat:{sender}:buffer"
    messages = r.get(key)
    if not messages:
        return

    print(messages)
    full_text = messages.decode("utf-8")
    r.delete(key)  # clear buffer

    

    chat, _ = Chat.objects.get_or_create(number=sender)

    # Save fused message
    user_message = Message.objects.create(chat=chat, text=full_text, from_user=True)

    # Orchestrate reply
    reply = Orchestrator().handle_message(full_text, chat)
    machine_message = Message.objects.create(chat=chat, text=reply, from_user=False)

    # Send reply
    if not debug:
        manager.send_message(sender, reply)
    elif sender=='51967244227':
        manager.send_message(sender, reply)
