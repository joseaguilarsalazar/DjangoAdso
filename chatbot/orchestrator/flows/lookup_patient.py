from chatbot.models import Chat
from core.models import Paciente

def lookup_patient(messages, chat: Chat):
    patients = chat.extra_data.get('patients', None)
    there_patient = True if len(patients) > 0 else False
    if chat.data_confirmed and len(patients) > 0:
        chat.current_state = 'default'
        chat.current_sub_state = 'default'
        chat.save()
        return """Veo que su informacion ya esta regisrada, digame por favor.
        ¿En qué puedo ayudarle hoy?"""
    if len(patients) == 0:
        number = chat.number.split('1')[1] if '1' in chat.number else chat.number
        if len(number) != 9:
             pass
        else:
            patient = Paciente.objects.filter(telf_pac=number).first()
        if not patient:
             pass
        else:
            chat.extra_data['patients'].append({
                'nombre': patient.nomb_pac,
                'apellido': patient.apel_pac,
                'dni': patient.dni_pac,
                'fecha_nacimiento': str(patient.fena_pac),
                'clinica_id': patient.clinica.id if patient.clinica else None,
                'patient_id': patient.id,
                'is_phone_owner': True if patient.telf_pac == number else False
            })
            chat.save()
            there_patient = True

    if not there_patient:
        chat.current_state = 'patient_registration'
        chat.current_sub_state = 'awaiting_data'
        chat.save()
        return f'''
        Veo que este numero no esta registrado en nuestro sistema,
        por favor envienos los siguientes datos para poder registrarlo:
        Nombre:
        Apellido:
        DNI:
        Fecha de Nacimiento:
    '''
    else:
        chat.current_state = 'data_confirmation'
        chat.current_sub_state = 'awaiting_confirmation'
        chat.save()
        if not patient:
            for person in patients:
                if person.get('is_phone_owner', False):
                    patient = Paciente.objects.get(id=person['patient_id'])
                    if patient:
                        break
        return f'''
        Por favor confirme que estos sean sus datos antes de continuar:
        Nombre: {patient.nomb_pac} {patient.apel_pac}
        DNI: {patient.dni_pac}    
        Fecha de Nacimiento: {patient.fena_pac}
        Numero de Telefono: {patient.telf_pac}
        Direccion: {patient.dire_pac}
        '''