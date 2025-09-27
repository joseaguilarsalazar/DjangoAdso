# chatbot/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chatbot.orchestrator.orchestrator import Orchestrator
from core.utils.EvolutionApiManager import EvolutionApiManager
from pathlib import Path
import os
import environ
from rest_framework.permissions import AllowAny
from .models import Chat, Message
env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = os.path.join(BASE_DIR, '.env')


if os.path.exists(env_file):
    environ.Env.read_env(env_file)

manager = EvolutionApiManager()

debug = env.bool('true_msg', default=False) 

class WhatsAppWebhookView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        payload = request.data

        

        # Extract incoming message info
        sender: str = payload.get("data", {}).get("key",{}).get('remoteJid') 
        
        text   = payload.get("data", {}).get("message",{}).get('conversation')

        if not sender or not text:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        
        sender = sender.split('@')[0] # WhatsApp number
        if "-" in sender:  # group chats have a hyphen
            return Response({"status": "ignored (group chat)"}, status=status.HTTP_200_OK)

        chat, created = Chat.objects.get_or_create(number=sender)
        user_message = Message.objects.create(chat=chat, text=text, from_user =True)
        user_message.save()

        # Process with chatbot orchestrator
        reply = Orchestrator().handle_message(text, chat)

        machine_message = Message.objects.create(chat=chat, text=reply, from_user =False)
        machine_message.save()

        # Send response back through Evolution API
        if not debug or sender == '51967244227':
            manager.send_message(sender, reply)


        return Response({"status": "ok"}, status=status.HTTP_200_OK)
