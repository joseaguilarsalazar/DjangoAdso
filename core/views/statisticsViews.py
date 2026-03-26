from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Cita, Tratamiento, TratamientoPaciente
from transactions.models import Ingreso, Egreso
from datetime import datetime, timedelta, date
from datetime import date as dt
from django.db.models import Sum
from django.db.models.functions import TruncDate, Concat
from django.db.models import Count, OuterRef, Q, Min, Subquery
from django.db.models import Value as V

class CitasHistogramaApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else date.today()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else date.today()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        # 1. Subquery: Find the absolute first appointment date for every patient
        first_appointments = Cita.objects.filter(
            paciente_id=OuterRef('paciente_id')
        ).order_by().values('paciente_id').annotate(
            first_date=Min('fecha')
        ).values('first_date')

        # 2. Base Queryset with 'is_new_patient' logic
        # We annotate each appointment with whether it matches the patient's first ever date
        queryset = Cita.objects.filter(fecha__range=[start_date, end_date]).annotate(
            first_ever_date=Subquery(first_appointments),
        ).annotate(
            is_new_patient=Q(fecha=Min('first_ever_date')) # Logical check
        )

        # 3. Optimized Daily Histogram
        # Now we count total, unique, and filter for those who are 'new'
        histogram_data = (
            queryset
            .annotate(day=TruncDate('fecha'))
            .values('day')
            .annotate(
                total_appointments=Count('id'),
                unique_patients=Count('paciente_id', distinct=True),
                # We only count IDs where the appointment date is the patient's first date
                new_patients=Count('id', filter=Q(fecha=OuterRef('first_ever_date')), distinct=True)
            )
            .order_by('day')
        )

        # 4. Doctor Aggregation (Same as before)
        doctor_data = (
            Cita.objects.filter(fecha__range=[start_date, end_date], medico__isnull=False)
            .annotate(full_name=Concat('medico__name', V(' '), 'medico__last_name'))
            .values('full_name')
            .annotate(count=Count('id'))
        )
        doctors_dict = {item['full_name']: item['count'] for item in doctor_data}

        return Response({
            "cita_count": list(histogram_data),
            "doctor": doctors_dict,
        })

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

        # 2. Prepare Filters (EXACTLY matching CierreDeCaja logic)
        # We filter by created_at__date__range
        ingreso_filters = {'created_at__date__range': [start_date, end_date]}
        egreso_filters = {'created_at__date__range': [start_date, end_date]}

        if tratamiento_id:
            tratamiento = Tratamiento.objects.filter(id=tratamiento_id).first()
            if tratamiento:
                tp_ids = TratamientoPaciente.objects.filter(tratamiento=tratamiento).values_list('id', flat=True)
                ingreso_filters['tratamientoPaciente__in'] = tp_ids
                egreso_filters['tratamientoPaciente__in'] = tp_ids

        # 3. Aggregation
        # We use TruncDate('created_at') to align perfectly with created_at__date
        
        ingresos_by_day = (
            Ingreso.objects.filter(**ingreso_filters)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(total=Sum('monto'))
            .order_by('day')
        )
        
        egresos_by_day = (
            Egreso.objects.filter(**egreso_filters)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(total=Sum('monto'))
            .order_by('day')
        )

        # 4. Map to Dictionary for O(1) Lookup
        ingresos_dict = {item['day']: item['total'] for item in ingresos_by_day}
        egresos_dict = {item['day']: item['total'] for item in egresos_by_day}
        total_ingresos = 0
        total_egresos = 0
        total_balance = 0

        # 5. Build Timeline
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Get values or default to 0
            day_ingreso = ingresos_dict.get(current_date, 0)
            day_egreso = egresos_dict.get(current_date, 0)

            total_ingresos += day_ingreso
            total_egresos += day_egreso
            total_balance += (day_ingreso - day_egreso)
            
            data.append({
                'date': current_date,
                'ingresos': day_ingreso,
                'egresos': day_egreso,
                'balance': day_ingreso - day_egreso
            })
            current_date += timedelta(days=1)
        
        final_data = {
            'timeline': data,
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'total_balance': total_balance
        }

        return Response(final_data)

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