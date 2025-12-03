from celery import shared_task
from django.conf import settings
from chatbot.orchestrator.orchestrator import Orchestrator
from chatbot.models import Chat, Message
from core.utils.chatwoot_manager import ChatwootManager
import redis
from pathlib import Path
import os
import environ
from djangoAdso.settings import REDIS_URL

manager = ChatwootManager()

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = os.path.join(BASE_DIR, '.env')


if os.path.exists(env_file):
    environ.Env.read_env(env_file)

r = redis.Redis.from_url(REDIS_URL)

test_senders = ['51967244227', #yo
                 '51930492745', #licenciado 
                 '51953656319', #Ale
                 '51972547142', #Cinthia
                 '51935433771', #Sara
                 ]  # Números permitidos para pruebas cuando true_chatbot es False

true_chatbot = env.bool('true_chatbot', default=False)

@shared_task
def process_user_buffer(sender: str, instance: str, conversation_id: int, contact_id: int):
    key = f"chat:{sender}:buffer"
    messages = r.get(key)
    if not messages:
        return

    full_text = messages.decode("latin-1")

    r.delete(key)  # clear buffer

    chat, _ = Chat.objects.get_or_create(number=sender)

    # Save fused message
    user_message = Message.objects.create(chat=chat, text=full_text, from_user=True)

    # Orchestrate reply
    reply = Orchestrator().handle_message(full_text, chat, instance=instance)
    reply += f"\n\n chat_state: {chat.current_state}, chat_sub_state: {chat.current_sub_state} #para el modelo, ignora esta ultima parte"
    machine_message = Message.objects.create(chat=chat, text=reply, from_user=False)

    # Send reply
    if true_chatbot:
        manager.send_message(sender, reply, message_instance=instance, conversation_id=conversation_id, contact_id=contact_id)
    elif sender in test_senders:
        manager.send_message(sender, reply, message_instance=instance, conversation_id=conversation_id, contact_id=contact_id)