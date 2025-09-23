from rest_framework import serializers
from .models import Ingreso
from core.models import Cita

class IngresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingreso
        fields = '__all__'

    def validate(self, attrs):
        """
        Enforce cita, paciente, medico required at creation,
        but still allow them to become null if the related objects are deleted.
        """
        if self.instance is None:  # creation
            required_fields = ["tratamientoPaciente", "medico"]
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError({
                        field: f"{field.capitalize()} is required when creating a pago."
                    })
        return attrs

        return pago