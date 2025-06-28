from rest_framework.serializers import ModelSerializer
from .models import (
    Diente,
    DienteOdontograma,
    CasoMultidental,
    Odontograma,
)


class DienteSerializer(ModelSerializer):
    class Meta:
        model = Diente
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class DienteOdontogramaSerializer(ModelSerializer):
    class Meta:
        model = DienteOdontograma
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class CasoMultidentalSerializer(ModelSerializer):
    class Meta:
        model = CasoMultidental
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class OdontogramaSerializer(ModelSerializer):
    class Meta:
        model = Odontograma
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']