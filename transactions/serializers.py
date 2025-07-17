from rest_framework import serializers
from .models import Pagos
from core.models import Cita

class PagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagos
        fields = '__all__'


    def create(self, validated_data):
        pago = Pagos.objects.create(**validated_data)
        pago.cita.pagado += pago.monto
        if pago.cita.pagado >= pago.cita.costo:
            pago.cita.estadoPago = 'PAGADO'
        elif pago.cita.pagado > 0 and pago.cita.estadoPago != 'PARCIAL':
            pago.cita.estadoPago = 'PARCIAL'
        return super().create(validated_data)