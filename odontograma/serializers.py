from rest_framework.serializers import ModelSerializer
from rest_framework import  serializers
from .models import (
    Diente,
    DienteOdontograma,
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

class DienteOdontogramaSerializer(serializers.ModelSerializer):
    icono_url = serializers.SerializerMethodField()

    class Meta:
        model = DienteOdontograma
        fields = fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_icono_url(self, obj):
        s3 = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1',
        )

        if not obj.iconoModificado:
            if obj.diente and obj.diente.iconoPorDefecto:
                key = obj.diente.iconoPorDefecto.name
            else:
                return None
        else:
            key = obj.iconoModificado.name

        try:
            return s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': key},
                ExpiresIn=3600,
            )
        except Exception:
            return None

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