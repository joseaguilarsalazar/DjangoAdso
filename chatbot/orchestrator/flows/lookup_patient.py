from chatbot.models import Chat
from core.models import Paciente

def lookup_patient(messages, chat: Chat):
    patient = chat.patient if chat.patient else None
    there_patient = True if patient else False
    if not patient:
        number = chat.number.split('1')[1] if '1' in chat.number else chat.number
        if len(number) != 9:
             pass
        else:
            patient = Paciente.objects.filter(telf_pac=number).first()
        if not patient:
             pass
        else:
            chat.patient = patient
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
        return f'''
        Por favor confirme que estos sean sus datos antes de continuar:
        Nombre: {patient.nomb_pac} {patient.apel_pac}
        DNI: {patient.dni_pac}    
        Fecha de Nacimiento: {patient.fena_pac}
        Numero de Telefono: {patient.telf_pac}
        Direccion: {patient.dire_pac}
        '''