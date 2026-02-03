
from .models import Ingreso, Egreso, TratamientoPaciente
from django.db import transaction
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Q, Sum

# --- INGRESO TRIGGERS ---
@receiver(post_save, sender=Ingreso)
def on_ingreso_change(sender, instance, created, **kwargs):
    """
    If a patient pays (or updates a payment), recalculate commissions.
    """
    if instance.tratamientoPaciente:
        recalculate_finances(instance.tratamientoPaciente.id)

@receiver(post_delete, sender=Ingreso)
def on_ingreso_delete(sender, instance, **kwargs):
    """
    If a payment is deleted, recalculate commissions (doctor might lose money).
    """
    if instance.tratamientoPaciente:
        recalculate_finances(instance.tratamientoPaciente.id)


# --- EGRESO TRIGGERS ---
@receiver(post_save, sender=Egreso)
def on_egreso_change(sender, instance, created, **kwargs):
    """
    If a Lab expense is added/changed, recalculate.
    If a Doctor Commission is changed, DO NOTHING (to avoid recursion).
    """
    
    # 1. CRITICAL: Recursion Guard
    # If the Egreso saved is a Doctor Commission ('DOC'), it means our 
    # service script just saved it. We must NOT trigger recalculation again, 
    # or we will enter an infinite loop.
    if instance.tipo == 'DOC':
        return

    # 2. If it's a Lab expense, the doctor's net might change.
    if (instance.tipo == 'LAB' and instance.tratamientoPaciente) or (instance.tratamientoPaciente and instance.medico == None):
        recalculate_finances(instance.tratamientoPaciente.id)

@receiver(post_delete, sender=Egreso)
def on_egreso_delete(sender, instance, **kwargs):
    """
    If a Lab expense is deleted, the doctor might get money back.
    """
    if instance.tipo == 'DOC':
        return # Deleting a commission shouldn't trigger recalc

    if instance.tipo == 'LAB' and instance.tratamientoPaciente:
        recalculate_finances(instance.tratamientoPaciente.id)


def recalculate_finances(tratamiento_id):
    with transaction.atomic():
        # 1. Lock records to prevent race conditions
        tratamiento = TratamientoPaciente.objects.select_for_update().get(pk=tratamiento_id)
        
        # 2. Get all money IN (Ordered by date)
        ingresos = Ingreso.objects.filter(tratamientoPaciente=tratamiento).order_by('created_at')
        
        # 3. Get TOTAL Lab Expenses
        # Count as Lab if type is 'LAB' OR if there is no doctor assigned (standard lab entry)
        lab_expenses_total = Egreso.objects.filter(
            tratamientoPaciente=tratamiento
        ).filter(
            Q(tipo='LAB') | Q(medico__isnull=True)
        ).aggregate(sum=Sum('monto'))['sum'] or Decimal(0)

        remaining_lab_debt = lab_expenses_total

        # ==============================================================================
        # 4. CRITICAL FIX: The "Catch-All" Wipe
        # ==============================================================================
        # We need to delete ANY doctor commission associated with this treatment.
        # This includes:
        #   1. New records (tipo='DOC')
        #   2. Old Legacy records (which might have tipo=NULL or tipo='CLI' by default)
        #
        # LOGIC: If it has a doctor assigned AND it is not a Lab expense, DELETE IT.
        Egreso.objects.filter(
            tratamientoPaciente=tratamiento,
            medico__isnull=False
        ).exclude(
            tipo='LAB'
        ).delete()
        # ==============================================================================

        # 5. Replay the history
        for ingreso in ingresos:
            # How much of this income is eaten by lab debt?
            deduction = min(ingreso.monto, remaining_lab_debt)
            net_profit = ingreso.monto - deduction
            
            # Decrease debt for next iteration
            remaining_lab_debt -= deduction

            # If there is profit, PAY THE DOCTOR
            if net_profit > 0 and ingreso.medico:
                # Logic for percentage
                if ingreso.porcentaje_medico:
                    pct = Decimal(str(ingreso.porcentaje_medico))
                else:
                    # FIX: Use 50/40 (Integers), not 0.5/0.4
                    pct = Decimal('50') if ingreso.medico.is_especialista else Decimal('40')
                
                # Calculation: (40 / 100) = 0.4
                amount = net_profit * (pct / 100)
                
                # Create the new, clean record
                Egreso.objects.create(
                    tipo='DOC',
                    source_ingreso=ingreso, 
                    monto=amount,
                    medico=ingreso.medico,
                    tratamientoPaciente=tratamiento,
                    description=f'Pago médico generado por ingreso {ingreso.id}',
                    fecha_registro=ingreso.fecha_registro
                )