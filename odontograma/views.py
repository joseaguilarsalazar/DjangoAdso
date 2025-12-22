from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Paciente
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


from .models import (
    Odontograma, 
    Diente,  
    CasoMultidental,
    Hallazgo,
    )

from .serializers import (
    OdontogramaSerializer, 
    DienteSerializer, 
    CasoMultidentalSerializer,
    HallazgoSerializer,
    )

from .filters import (
    OdontogramaFilter, 
    DienteFilter, 
    CasoMultidentalFilter,
    HallazgoFilter,
    )
# Create your views here.


class OdontogramaViewSet(viewsets.ModelViewSet):
    queryset = Odontograma.objects.all().order_by('id')
    serializer_class = OdontogramaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OdontogramaFilter
    ordering_fields = '__all__'

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        paciente_nombre = request.query_params.get('paciente_nombre')

        if paciente_nombre:
            pacientes = Paciente.objects.all()
            concidences = [p for p in pacientes if paciente_nombre.lower() in str(p.__str__()).lower()]
            return_list = []

            for paciente in concidences:
                odontograma = Odontograma.objects.filter(paciente_id=paciente.id).first()
                if odontograma:
                    return_list.append(odontograma)

            serializer = self.get_serializer(return_list, many=True)
            return Response(serializer.data)

        return super().list(request, *args, **kwargs)

class DienteViewSet(viewsets.ModelViewSet):
    queryset = Diente.objects.all().order_by('id')
    serializer_class = DienteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = DienteFilter
    ordering_fields = '__all__'

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated()]


class CasoMultidentalViewSet(viewsets.ModelViewSet):
    queryset = CasoMultidental.objects.all().order_by('id')
    serializer_class = CasoMultidentalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CasoMultidentalFilter
    ordering_fields = '__all__'

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated()]
    

class HallazgoViewSet(viewsets.ModelViewSet):
    queryset = Hallazgo.objects.all().order_by('id')
    serializer_class = HallazgoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = HallazgoFilter
    ordering_fields = '__all__'

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsAuthenticated()]
    


class OdontogramaAPIView(APIView):
    
    def get(self, request, paciente_id):
        """
        Get the LATEST odontograma for this patient.
        Returns the data in the exact format the React component expects.
        """
        # 1. Try to find the latest odontograma
        odontograma = Odontograma.objects.filter(paciente_id=paciente_id).order_by('-created_at').first()

        if not odontograma:
            # If none exists, return empty structure so frontend loads a blank canvas
            return Response({
                "drawings": {},
                "toothStates": {},
                "especificaciones": "",
                "observaciones": ""
            }, status=status.HTTP_200_OK)

        # 2. Transform Hallazgos (Rows) -> toothStates (JSON)
        # We turn [Hallazgo(diente=18, condicion='CARR'), ...] into { "18": "CARR", ... }
        tooth_states = {
            str(h.diente.numero): h.condicion 
            for h in odontograma.hallazgos.all()
        }

        # 3. Return Payload
        return Response({
            "drawings": odontograma.drawings,  # Already JSON in DB
            "toothStates": tooth_states,       # Transformed Dict
            "especificaciones": odontograma.especificaciones,
            "observaciones": odontograma.observaciones,
            "id": odontograma.id,              # Useful for updates
            "updated_at": odontograma.updated_at
        })

    def post(self, request, paciente_id):
        """
        Create or Update the Odontograma.
        We use a 'Wipe and Replace' strategy for Hallazgos to keep sync simple.
        """
        data = request.data
        
        paciente = get_object_or_404(Paciente, pk=paciente_id)

        # 1. Update existing or Create new Odontograma for this patient
        # (You might want logic here: "Create new one every day?" vs "Update the single existing one?")
        # For now, let's assume we Update the latest one if it exists, or create new.
        odontograma = Odontograma.objects.filter(paciente=paciente).order_by('-created_at').first()

        if not odontograma:
            odontograma = Odontograma(paciente=paciente)
        
        # 2. Save Basic Fields
        odontograma.drawings = data.get('drawings', {})
        odontograma.especificaciones = data.get('especificaciones', '')
        odontograma.observaciones = data.get('observaciones', '')
        odontograma.save()

        # 3. Save Hallazgos (The Tooth Codes)
        # Strategy: Delete old codes for this chart and re-insert the current state.
        # This prevents "Zombie codes" (codes you deleted in frontend but stay in DB).
        
        current_states = data.get('toothStates', {}) # { "18": "CARR", "21": "SANA" }
        
        # Wipe old
        odontograma.hallazgos.all().delete()

        # Insert new
        hallazgos_buffer = []
        for tooth_num_str, code in current_states.items():
            if not code: continue # Skip empty codes

            try:
                # Ensure Diente exists in your static table (Create if missing for safety)
                diente_obj, _ = Diente.objects.get_or_create(numero=int(tooth_num_str), defaults={'hitbox_json': {}})
                
                hallazgos_buffer.append(
                    Hallazgo(
                        odontograma=odontograma,
                        diente=diente_obj,
                        condicion=code
                        # estado='BAD' if code in ['CARR', 'EXTR'] else 'GOOD' # Optional Auto-logic
                    )
                )
            except ValueError:
                continue # Skip invalid keys
        
        # Bulk create is much faster than saving one by one
        Hallazgo.objects.bulk_create(hallazgos_buffer)

        return Response({"message": "Odontograma guardado correctamente"}, status=status.HTTP_200_OK)