# chatbot/api/views.py
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

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_file):
    environ.Env.read_env(env_file)

r = redis.Redis.from_url(REDIS_URL)

class WhatsAppWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        
        # --- 1. Chatwoot Event Filtering ---
        # Chatwoot sends webhooks for outgoing messages and status updates too.
        # We only want 'message_created' and specifically 'incoming' messages.
        event_type = payload.get('event')
        message_type = payload.get('message_type')

        if event_type != 'message_created' or message_type != 'incoming':
            # Return 200 to acknowledge receipt, but do nothing
            return Response({"status": "ignored (not incoming message)"}, status=status.HTTP_200_OK)

        # --- 2. Sender Extraction ---
        # Chatwoot provides sender info in the 'sender' object.
        # Format usually comes as "+123456789". We remove the '+' to match typical ID formats.
        sender_data = payload.get('sender', {})
        sender_phone = sender_data.get('phone_number')
        
        if not sender_phone:
             return Response({"error": "No sender phone found"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove '+' and use as ID (e.g. +5511999 -> 5511999)
        sender = sender_phone.replace('+', '')

        # Map Chatwoot Inbox ID to "Instance"
        # Using the Inbox ID ensures unique processing if you have multiple WhatsApp numbers connected.
        inbox = payload.get('inbox', {})
        instance = str(inbox.get('id', 'testing_instance'))

        # --- 3. Content Extraction ---
        text = payload.get('content')
        attachments = payload.get('attachments', [])
        
        audio_url = None
        # Check if there are attachments and if one of them is audio
        if attachments:
            for attachment in attachments:
                if attachment.get('file_type') == 'audio':
                    audio_url = attachment.get('data_url')
                    break

        # Validation: Must have either text or audio
        if not text and not audio_url:
             return Response({"error": "Empty message content"}, status=status.HTTP_200_OK)

        # --- 4. Audio Processing (Deepgram) ---
        if audio_url:
            print(f"Processing audio from: {audio_url}")
            
            try:
                # Download audio file from Chatwoot/AWS S3 URL
                audio_response = requests.get(audio_url)
                
                if audio_response.status_code != 200:
                    print(f"Failed to download audio: {audio_response.status_code}")
                    return Response({"error": "Failed to download audio"}, status=status.HTTP_400_BAD_REQUEST)
                
                audio_bytes = audio_response.content

                # Send to Deepgram API
                dg_url = "https://api.deepgram.com/v1/listen?model=nova-3&smart_format=true"
                headers = {
                    "Authorization": f"Token {env('deepgram_key')}",
                    # Chatwoot usually saves WhatsApp voice notes as audio/ogg
                    "Content-Type": "audio/ogg" 
                }
                
                resp = requests.post(dg_url, headers=headers, data=audio_bytes)

                if resp.status_code != 200:
                    print(f"Deepgram Error: {resp.text}")
                    return Response(
                        {"error": "Deepgram transcription failed", "details": resp.text},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                dg_result = resp.json()
                # Fallback in case deepgram returns empty results for noise
                if dg_result.get("results"):
                    text = dg_result["results"]["channels"][0]["alternatives"][0]["transcript"]
                    print(f"Transcribed: {text}")
                else:
                    text = "[Audio unintelligible]"

            except Exception as e:
                print(f"Error processing audio: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # --- 5. Redis Buffering ---
        # Ensure text is not None before buffering
        if not text: 
            text = ""

        key = f"chat:{sender}:buffer"
        pipe = r.pipeline()
        # Note: Added a space before text to separate multiple messages in buffer
        pipe.append(key, f" {text}") 
        pipe.expire(key, 30)  # reset timer
        pipe.execute()

        print(f"Buffered for {sender}: {r.get(key)}")

        # --- 6. Celery Task ---
        process_user_buffer.apply_async((sender, instance,), countdown=10)

        return Response({"status": "buffered"}, status=status.HTTP_200_OK)