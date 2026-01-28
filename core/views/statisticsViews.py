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
            
        dates = []
        current_date = start_date
        data = []
        
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
            
        # Optimization: Fetch all citas in range once, then process in memory
        # CAUTION: Check your Cita model. Is the field 'fecha', 'fecha_cita', or 'fecha_registro'?
        # I am assuming 'fecha' based on your old code, but if it crashes, check this field name!
        all_citas = Cita.objects.filter(fecha__range=[start_date, end_date])
        
        for date_obj in dates:
            # Filter the pre-fetched list for the current date
            day_citas = [c for c in all_citas if c.fecha == date_obj]
            
            if unique_patient_filter:
                unique_patients = {c.paciente.id for c in day_citas}
                data.append({'date': date_obj, 'count': len(unique_patients)})
            else:
                data.append({'date': date_obj, 'count': len(day_citas)})
                
        return Response(data)

class IngresosEgresosHistogramaApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        tratamiento_id = request.query_params.get('tratamiento_id')
        
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date = dt.today()

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date = dt.today()
            
        dates = []
        current_date = start_date
        data = []

        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)

        # Optimization: Fetch all transactions in range
        # FIX: Changed 'fecha' to 'fecha_registro'
        all_ingresos = Ingreso.objects.filter(fecha_registro__range=[start_date, end_date])
        all_egresos = Egreso.objects.filter(fecha_registro__range=[start_date, end_date])

        # Apply Tratamiento filter if needed
        if tratamiento_id:
            tratamiento = Tratamiento.objects.filter(id=tratamiento_id).first()
            if tratamiento:
                tp_ids = TratamientoPaciente.objects.filter(tratamiento=tratamiento).values_list('id', flat=True)
                # Ensure Ingreso has 'tratamientoPaciente' FK as defined in your model
                all_ingresos = all_ingresos.filter(tratamientoPaciente__in=tp_ids)
                all_egresos = all_egresos.filter(tratamientoPaciente__in=tp_ids)

        for date_obj in dates:
            # FIX: Changed 'fecha' to 'fecha_registro'
            daily_ingresos = [i for i in all_ingresos if i.fecha_registro == date_obj]
            daily_egresos = [e for e in all_egresos if e.fecha_registro == date_obj]
            
            total_ingresos = sum(i.monto for i in daily_ingresos)
            total_egresos = sum(e.monto for e in daily_egresos)
            
            data.append({
                'date': date_obj, 
                'ingresos': total_ingresos, 
                'egresos': total_egresos, 
                'balance': total_ingresos - total_egresos
            })

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
        
        # Ensure TratamientoPaciente has 'created_at' or change to 'fecha_registro'
        tratamientos_paciente = TratamientoPaciente.objects.filter(
            created_at__date__gte=start_date, 
            created_at__date__lte=end_date
        ).select_related('tratamiento') # Optimization

        for tp in tratamientos_paciente:
            t_name = tp.tratamiento.nombre
            
            if t_name not in data:
                data[t_name] = {
                    'total_ingresos': 0.0,
                    'total_egresos': 0.0,
                    'net_balance': 0.0,
                    'count': 0
                }
            
            # Using the reverse relationship name 'ingresos' from your model definition:
            # related_name='ingresos'
            ingresos = tp.ingresos.all() 
            
            # Assuming Egreso also has a FK to TratamientoPaciente?
            # If not, this line below will crash. Check your Egreso model.
            egresos = Egreso.objects.filter(tratamientoPaciente=tp) 

            # Calculate sums
            # Use 'or 0' to handle None if database field allows nulls
            sum_ing = sum(i.monto for i in ingresos) or 0 
            sum_egr = sum(e.monto for e in egresos) or 0
            
            data[t_name]['total_ingresos'] += float(sum_ing)
            data[t_name]['total_egresos'] += float(sum_egr)
            data[t_name]['net_balance'] += float(sum_ing - sum_egr)
            data[t_name]['count'] += 1
            
        return Response(data)