from rest_framework import serializers
from .models import Ingreso
from ..core.models import Paciente
from core.models import TratamientoPaciente  # add import
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db import transaction
from django.contrib.auth import get_user_model
User = get_user_model()
class IngresoSerializer(serializers.ModelSerializer):
    # frontend can send paciente id instead of full tratamientoPaciente object
    paciente = serializers.IntegerField(write_only=True, required=False, queryset=Paciente.objects.all())
    medico = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = Ingreso
        fields = '__all__'
        depth = 1  # Include related objects up to 1 levels deep

    def validate(self, attrs):
        """
        Enforce medico required at creation.
        Allow frontend to provide 'paciente' id instead of tratamientoPaciente.
        """
        if self.instance is None:  # creation
            # Either tratamientoPaciente must be provided or paciente id must be provided
            if not attrs.get("tratamientoPaciente") and not attrs.get("paciente"):
                raise serializers.ValidationError({
                    "tratamientoPaciente": "Provide either tratamientoPaciente or paciente id when creating an ingreso."
                })
            if not attrs.get("medico"):
                raise serializers.ValidationError({
                    "medico": "Medico is required when creating an ingreso."
                })
            if not attrs.get("monto"):
                raise serializers.ValidationError({
                    "monto": "Monto is required when creating an ingreso."
                })
        return attrs

    def _find_unpaid_tratamientos_qs(self, paciente_id):
        """
        Return queryset of TratamientoPaciente for paciente annotated with paid sum,
        ordered by created_at (oldest first).
        """
        qs = TratamientoPaciente.objects.filter(paciente_id=paciente_id).annotate(
            paid=Coalesce(Sum('ingreso__monto'), 0.0)
        ).order_by('created_at')
        return qs

    def _tratamiento_total_price(self, tp: TratamientoPaciente):
        """
        Compute total price for a TratamientoPaciente instance:
         - use tratamiento.precioConvenio when tp.convenio and precioConvenio exists,
           otherwise tratamiento.precioBase
         - apply tp.descuento: if 0 <= descuento <= 1 treat as percentage, else absolute amount
        """
        base = tp.tratamiento.precioConvenio if (tp.convenio and tp.tratamiento.precioConvenio) else tp.tratamiento.precioBase
        try:
            descuento = float(tp.descuento)/100 if tp.descuento <= 100 else 1.0
        except Exception:
            descuento = 0.0
        if not tp.descuento_porcentaje:
            descuento = tp.descuento or 0.0
        if 0.0 < descuento <= 1.0:
            total = base * (1.0 - descuento)
        else:
            total = max(base - descuento, 0.0)
        return float(total)

    @transaction.atomic
    def create(self, validated_data):
        paciente_id = validated_data.pop('paciente_id', None)
        provided_tp = validated_data.get('tratamientoPaciente_id', None)

        # If frontend gave a paciente id and didn't specify tratamientoPaciente,
        # allocate the monto across oldest unpaid TratamientoPaciente objects.
        if paciente_id and not provided_tp:
            monto_to_allocate = validated_data.pop('monto')
            if monto_to_allocate is None:
                raise serializers.ValidationError({"monto": "Monto is required to allocate payments."})
            try:
                monto_remaining = float(monto_to_allocate)
            except Exception:
                raise serializers.ValidationError({"monto": "Monto must be a number."})

            medico = validated_data.get('medico', None)
            metodo = validated_data.get('metodo', None)

            created_ingresos = []

            qs = self._find_unpaid_tratamientos_qs(paciente_id)

            for tp in qs:
                total_price = self._tratamiento_total_price(tp)
                paid = float(getattr(tp, 'paid', 0.0) or 0.0)
                remaining_tp = total_price - paid
                if remaining_tp <= 0:
                    continue
                allocate = min(remaining_tp, monto_remaining)
                ingreso_data = {
                    'tratamientoPaciente': tp,
                    'monto': allocate,
                    'medico': medico,
                    'metodo': metodo,
                }
                # create ingreso for this tratamiento
                ingreso_obj = Ingreso.objects.create(**{k: v for k, v in ingreso_data.items()})
                created_ingresos.append(ingreso_obj)
                monto_remaining -= allocate
                if monto_remaining <= 0:
                    break

            # If there's leftover monto and no tratamientos to assign, create ingreso w/o tratamientoPaciente
            if monto_remaining > 0:
                ingreso_data = {
                    'tratamientoPaciente': None,
                    'monto': monto_remaining,
                    'medico': validated_data.get('medico', None),
                    'metodo': validated_data.get('metodo', None),
                }
                ingreso_obj = Ingreso.objects.create(**{k: v for k, v in ingreso_data.items()})
                created_ingresos.append(ingreso_obj)
                monto_remaining = 0.0

            if not created_ingresos:
                raise serializers.ValidationError({"paciente": "No unpaid TratamientoPaciente found and nothing created."})

            # Return the first created ingreso instance (DRF expects a model instance)
            return created_ingresos[0]

        # Fallback: default behavior when tratamientoPaciente is provided (or no paciente)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Keep update simple: if frontend wants to reallocate a payment, they should POST a new ingreso.
        paciente_id = validated_data.pop('paciente', None)
        if paciente_id and not validated_data.get('tratamientoPaciente'):
            raise serializers.ValidationError({
                "paciente": "Reallocation on update is not supported. Create a new ingreso (POST) to allocate to tratamientos."
            })
        return super().update(instance, validated_data)