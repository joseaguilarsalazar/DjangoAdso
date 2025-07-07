from rest_framework import serializers
from .models import Pagos

class PagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagos
        fields = '__all__'