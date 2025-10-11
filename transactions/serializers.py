from rest_framework import serializers
from .models import Ingreso
from core.models import TratamientoPaciente, Paciente # add import
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db import transaction
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.response import Response
class IngresoSerializer(serializers.ModelSerializer):
    # frontend can send paciente id instead of full tratamientoPaciente object
    # start with an empty queryset, populate per-request in __init__
    paciente = serializers.PrimaryKeyRelatedField(write_only=True, required=False, queryset=Paciente.objects.none())
    medico = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request') if hasattr(self, 'context') else None
        if not request or not getattr(request, 'user', None) or not request.user.is_authenticated:
            # leave default (no pacientes) for unauthenticated requests
            return
        user = request.user

        # build TratamientoPaciente queryset annotated with paid sum
        tp_qs = TratamientoPaciente.objects.annotate(
            paid=Coalesce(Sum('ingresos__monto'), 0.0)
        )
        # if TratamientoPaciente has a 'medico' field, filter by logged user
        if 'medico' in [f.name for f in TratamientoPaciente._meta.get_fields()]:
            tp_qs = tp_qs.filter(medico_id=user.id)

        paciente_ids = set()
        # iterate to compute total per tratamiento using existing helper
        for tp in tp_qs.select_related('tratamiento', 'paciente'):
            try:
                total = self._tratamiento_total_price(tp)
            except Exception:
                # skip if calculation fails for any tp
                continue
            paid = float(getattr(tp, 'paid', 0.0) or 0.0)
            if total - paid > 0:
                paciente_ids.add(tp.paciente_id)

        self.fields['paciente'].queryset = Paciente.objects.filter(id__in=paciente_ids)

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
            paid=Coalesce(Sum('ingresos__monto'), 0.0)
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
        # remove the write-only 'paciente' field so it isn't passed to Ingreso.objects.create()
        paciente = validated_data.pop('paciente', None)
        paciente_id = paciente.id if paciente is not None else None
        provided_tp = validated_data.get('tratamientoPaciente', None)

        # If frontend gave a paciente (id) and didn't specify tratamientoPaciente,
        # allocate the monto across oldest unpaid TratamientoPaciente objects.
        if paciente_id and not provided_tp:
            monto_to_allocate = validated_data.pop('monto', None)
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
                ingreso_obj = Ingreso.objects.create(**ingreso_data)
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
                ingreso_obj = Ingreso.objects.create(**ingreso_data)
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


    def list(self):
        queryset: list[TratamientoPaciente] = self.get_queryset()
        if queryset is None:
            return Response([])
        data = self.get_serializer(queryset, many=True).data

        for value in data:
            value['paciente'] = f'{Paciente.objects.get(id=value['tratamientoPaciente']['paciente']['id']).nomb_pac} {Paciente.objects.get(id=value['tratamientoPaciente']['paciente']['id']).apel_pac}'
            value['medico'] = User.objects.get(id=value['medico']['id']).username
        return Response(data, status=200)