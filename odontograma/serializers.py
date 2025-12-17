from rest_framework.serializers import ModelSerializer
from rest_framework import  serializers
from .models import (
    Diente,
    CasoMultidental,
    Odontograma,
)
from django.conf import settings
import boto3
from botocore.client import Config


class DienteSerializer(ModelSerializer):
    class Meta:
        model = Diente
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