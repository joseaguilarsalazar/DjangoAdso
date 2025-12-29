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
    permission_classes = [IsAdminUser] # Solo admins pueden hacer esto

    def post(self, request):
        # Opcional: Recibir confirmación o filtro en el body
        confirm = request.data.get('confirm', False)
        
        if not confirm:
            return Response({
                "error": "Seguridad: Debes enviar 'confirm': true en el cuerpo para iniciar un envío masivo."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Disparar la tarea de Celery asíncronamente
        task = enviar_encuesta_masiva_task.delay()

        return Response({
            "message": "Campaña de encuestas iniciada en segundo plano.",
            "task_id": task.id,
            "status": "processing"
        }, status=status.HTTP_202_ACCEPTED)