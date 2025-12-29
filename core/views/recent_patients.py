from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from datetime import timedelta
from core.models import Cita

class RecentPatientsCountView(APIView):
    """
    Returns the count of unique patients who had an appointment in the last X days.
    Usage: GET /api/stats/recent-patients/?days=30
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 1. Get 'days' parameter (Default to 30 if missing)
        try:
            days = int(request.query_params.get('days', 30))
        except ValueError:
            return Response({"error": "Parameter 'days' must be an integer"}, status=400)

        # 2. Calculate the cutoff date
        # We use .date() because Cita.fecha is likely a DateField, not DateTimeField
        cutoff_date = timezone.now().date() - timedelta(days=days)

        # 3. Count Unique Patients
        # filter(fecha__gte=...) gets appointments from that date onwards
        # values('paciente') groups by patient ID
        # distinct().count() ensures we count people, not appointments
        unique_count = Cita.objects.filter(
            fecha__gte=cutoff_date
        ).values('paciente').distinct().count()

        return Response({
            "days": days,
            "unique_patients_count": unique_count,
            "since_date": cutoff_date.strftime('%Y-%m-%d')
        })