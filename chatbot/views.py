# chatbot/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
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

r = redis.Redis.from_url(settings.REDIS_URL)

class WhatsAppWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        sender: str = payload.get("data", {}).get("key", {}).get("remoteJid")

        # WhatsApp text
        text = payload.get("data", {}).get("message", {}).get("conversation")

        # WhatsApp audio
        audio_message = payload.get("data", {}).get("message", {}).get("audioMessage")

        if not sender or (not text and not audio_message):
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

        sender = sender.split('@')[0]
        if "-" in sender:  # Ignore group messages
            return Response({"status": "ignored (group chat)"}, status=status.HTTP_200_OK)

        # If it's an audio message, download and transcribe with Deepgram
        if audio_message:
            media_url = audio_message.get("url")  # Adjust field based on Evolution API payload
            if not media_url:
                return Response({"error": "No audio URL found"}, status=status.HTTP_400_BAD_REQUEST)

            # Download audio file from WhatsApp/Evolution API
            audio_bytes = requests.get(media_url).content

            # Send to Deepgram API
            dg_url = "https://api.deepgram.com/v1/listen?model=nova-3&smart_format=true"
            headers = {
                "Authorization": f"Token {env('deepgram_key')}",
                "Content-Type": "audio/ogg"  # or "audio/wav" / "audio/mp4" depending on WhatsApp media
            }
            resp = requests.post(dg_url, headers=headers, data=audio_bytes)

            if resp.status_code != 200:
                return Response(
                    {"error": "Deepgram transcription failed", "details": resp.text},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            dg_result = resp.json()
            text = dg_result["results"]["channels"][0]["alternatives"][0]["transcript"]
            print(text)

        # Store (text or transcribed audio) in Redis buffer
        key = f"chat:{sender}:buffer"
        pipe = r.pipeline()
        pipe.append(key, f" {text}")
        pipe.expire(key, 30)  # reset timer
        pipe.execute()

        print(r.get(key))

        # Schedule Celery task
        process_user_buffer.apply_async((sender,), countdown=30)

        return Response({"status": "buffered"}, status=status.HTTP_200_OK)
