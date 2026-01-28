from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Cita, Tratamiento, TratamientoPaciente
from transactions.models import Ingreso, Egreso
from datetime import datetime, timedelta
from datetime import date as dt
from django.db.models import Sum, DateField
from django.db.models.functions import Coalesce, Cast

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

        # 1. Parse Dates
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date = dt.today()

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date = dt.today()

        # 2. Define the "Effective Date" logic
        # This tells DB: Use fecha_registro. If NULL, extract the Date from created_at.
        effective_date_annotation = Coalesce(
            'fecha_registro', 
            Cast('created_at', DateField())
        )

        # 3. Base Querysets with Annotation
        ingresos_qs = Ingreso.objects.annotate(dia=effective_date_annotation)
        egresos_qs = Egreso.objects.annotate(dia=effective_date_annotation)

        # 4. Filter by Date Range
        ingresos_qs = ingresos_qs.filter(dia__range=[start_date, end_date])
        egresos_qs = egresos_qs.filter(dia__range=[start_date, end_date])

        # 5. Optional: Filter by Tratamiento
        if tratamiento_id:
            tratamiento = Tratamiento.objects.filter(id=tratamiento_id).first()
            if tratamiento:
                tp_ids = TratamientoPaciente.objects.filter(tratamiento=tratamiento).values_list('id', flat=True)
                ingresos_qs = ingresos_qs.filter(tratamientoPaciente__in=tp_ids)
                egresos_qs = egresos_qs.filter(tratamientoPaciente__in=tp_ids)

        # 6. Aggregate (Group by Day and Sum)
        # This returns: [{'dia': 2026-01-28, 'total': 3586.00}, ...]
        ingresos_data = (
            ingresos_qs.values('dia')
            .annotate(total=Sum('monto'))
            .order_by('dia')
        )
        
        egresos_data = (
            egresos_qs.values('dia')
            .annotate(total=Sum('monto'))
            .order_by('dia')
        )

        # Convert to dictionaries for fast matching: { date: amount }
        ing_dict = {item['dia']: item['total'] for item in ingresos_data}
        egr_dict = {item['dia']: item['total'] for item in egresos_data}

        # 7. Build the final timeline
        data = []
        current_date = start_date
        while current_date <= end_date:
            day_ingreso = ing_dict.get(current_date, 0)
            day_egreso = egr_dict.get(current_date, 0)
            
            data.append({
                'date': current_date,
                'ingresos': day_ingreso,
                'egresos': day_egreso,
                'balance': day_ingreso - day_egreso
            })
            current_date += timedelta(days=1)

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