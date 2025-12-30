from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from core.tasks import enviar_encuesta_masiva_task

class TriggerSurveyBroadcastView(APIView):
    """
    Endpoint para iniciar el envío masivo de encuestas.
    POST /api/marketing/send-survey/
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        confirm = request.data.get('confirm', False)
        # Capture the specific number for testing (optional)
        test_number = request.data.get('number', None) 
        
        if not confirm:
            return Response({
                "error": "Seguridad: Debes enviar 'confirm': true en el cuerpo para iniciar el envío."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Pass the test_number to the Celery task
        # If test_number is None, the task should default to sending to everyone
        task = enviar_encuesta_masiva_task.delay(target_number=test_number)

        # Determine message based on mode
        mode_message = f"Modo TEST: Enviando únicamente a {test_number}" if test_number else "Modo MASIVO: Iniciando envío a toda la base de usuarios"

        return Response({
            "message": mode_message,
            "task_id": task.id,
            "status": "processing",
            "target": test_number if test_number else "all"
        }, status=status.HTTP_202_ACCEPTED)