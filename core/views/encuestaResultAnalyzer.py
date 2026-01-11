from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.tasks import analyze_survey_responses_task # We will create this

class EncuestaStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_number = request.data.get('number', None)
        year = request.data.get('year', None) 
        
        # Trigger the background task
        task = analyze_survey_responses_task.delay(target_number=target_number, year=year)

        return Response({
            "message": "Analysis started in background.",
            "task_id": task.id,
            "status": "processing",
            "target": target_number if target_number else "all"
        }, status=status.HTTP_202_ACCEPTED)