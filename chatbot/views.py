from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from djangoAdso.settings import REDIS_URL
import redis
import requests
from chatbot.tasks import process_user_buffer
from pathlib import Path
import os
import environ

env = environ.Env(DEBUG=(bool, False))
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

r = redis.Redis.from_url(REDIS_URL)

class WhatsAppWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        
        # 1. Filter: Only 'message_created' and 'incoming'
        event_type = payload.get('event')
        message_type = payload.get('message_type')

        if event_type != 'message_created' or message_type != 'incoming':
            return Response({"status": "ignored"}, status=status.HTTP_200_OK)

        # 2. Extract Data
        sender_data = payload.get('sender', {})
        sender_phone = sender_data.get('phone_number')
        
        # Extract Contact ID (This is the Chatwoot ID, e.g., 1, 55, etc.)
        contact_id = sender_data.get('id')

        if not sender_phone:
             return Response({"error": "No sender phone"}, status=status.HTTP_400_BAD_REQUEST)
        
        sender = sender_phone.replace('+', '')
        
        # Extract Conversation ID directly
        conversation_data = payload.get('conversation', {})
        conversation_id = conversation_data.get('id')
        
        inbox = payload.get('inbox', {})
        instance = str(inbox.get('id', 'testing_instance'))

        # 3. Content Extraction
        text = payload.get('content')
        attachments = payload.get('attachments', [])
        audio_url = None
        
        if attachments:
            for attachment in attachments:
                if attachment.get('file_type') == 'audio':
                    audio_url = attachment.get('data_url')
                    break

        if not text and not audio_url:
             return Response({"status": "empty"}, status=status.HTTP_200_OK)

        # 4. Audio Processing (Deepgram)
        if audio_url:
            try:
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    dg_url = "https://api.deepgram.com/v1/listen?model=nova-3&smart_format=true"
                    headers = {
                        "Authorization": f"Token {env('deepgram_key')}",
                        "Content-Type": "audio/ogg" 
                    }
                    resp = requests.post(dg_url, headers=headers, data=audio_response.content)
                    if resp.status_code == 200:
                        dg_result = resp.json()
                        if dg_result.get("results"):
                            text = dg_result["results"]["channels"][0]["alternatives"][0]["transcript"]
            except Exception as e:
                print(f"Audio Error: {e}")

        if not text: text = ""

        # 5. Buffer
        key = f"chat:{sender}:buffer"
        pipe = r.pipeline()
        pipe.append(key, f" {text}") 
        pipe.expire(key, 30)
        pipe.execute()

        # 6. Trigger Task
        # Passing: Phone, Instance/Inbox, Conv ID, Contact ID
        process_user_buffer.apply_async((sender, instance, conversation_id, contact_id), countdown=10)

        return Response({"status": "buffered"}, status=status.HTTP_200_OK)