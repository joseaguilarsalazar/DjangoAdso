from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Cita, Tratamiento, TratamientoPaciente
from transactions.models import Ingreso, Egreso
from datetime import datetime, timedelta
from datetime import date as dt

class CitasHistogramaApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        unique_patient_filter = request.query_params.get('unique_patient', 'false').lower() == 'true'

        
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date = dt.today()

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date = dt.today()
        dates = [] #an array of dates between start_date and end_date
        current_date = start_date
        data = []
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        if unique_patient_filter:
            for date in dates:
                citas = Cita.objects.filter(fecha=date)
                unique_patients = set()
                for cita in citas:
                    unique_patients.add(cita.paciente.id)
                data.append({'date': date, 'count': len(unique_patients)})
        else:
            for date in dates:
                citas = Cita.objects.filter(fecha=date)
                data.append({'date': date, 'count': citas.count()})
        return Response(data)

class IngresosEgresosHistogramaApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        tratamiento_id = request.query_params.get('tratamiento_id')
        tratamiento = Tratamiento.objects.filter(id=tratamiento_id).first() if tratamiento_id else None

        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date = dt.today()

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date = dt.today()
        dates = []
        data = []
        current_date = start_date

        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)

        for date in dates:
            if not tratamiento:
                ingresos = Ingreso.objects.filter(fecha=date)
                egresos = Egreso.objects.filter(fecha=date)
            else:
                tratamientos_paciente = TratamientoPaciente.objects.filter(tratamiento=tratamiento).values_list('paciente_id', flat=True)
                ingresos = Ingreso.objects.filter(fecha=date, paciente_id__in=tratamientos_paciente)
                egresos = Egreso.objects.filter(fecha=date, paciente_id__in=tratamientos_paciente)
            total_ingresos = sum([ingreso.monto for ingreso in ingresos])
            total_egresos = sum([egreso.monto for egreso in egresos])
            balance = total_ingresos - total_egresos
            data.append({'date': date, 'ingresos': total_ingresos, 'egresos': total_egresos, 'balance': balance})

        return Response(data)

class TratamientoStatisticsApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date = dt.today()

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date = dt.today()

        data = {}
        
        tratamientos = TratamientoPaciente.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

        for tratamiento in tratamientos:
            tratamiento_name = tratamiento.tratamiento.nombre
            if tratamiento_name not in data:
                data[tratamiento_name] = {
                    'total_ingresos': 0.0,
                    'total_egresos': 0.0,
                    'net_balance': 0.0,
                    'count': 0
                }
            ingresos = Ingreso.objects.filter(tratamientoPaciente=tratamiento)
            egresos = Egreso.objects.filter(tratamientoPaciente=tratamiento)

            total_ingresos = sum([ingreso.monto for ingreso in ingresos])
            total_egresos = sum([egreso.monto for egreso in egresos])
            net_balance = total_ingresos - total_egresos

            data[tratamiento_name]['total_ingresos'] += total_ingresos
            data[tratamiento_name]['total_egresos'] += total_egresos
            data[tratamiento_name]['net_balance'] += net_balance
            data[tratamiento_name]['count'] += 1
        return Response(data)