from django.contrib.auth import get_user_model
from ..models import Paciente, Tratamiento, Cita
from ..serializers import PacienteSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

@swagger_auto_schema(
    method='post',
    operation_summary="Cargar costo de tratamiento",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['tratamiento'],
        properties={
            'tratamiento': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del tratamiento'),
        },
    ),
    responses={
        200: openapi.Response(description="Costo del tratamiento", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'costo': openapi.Schema(type=openapi.TYPE_NUMBER)}
        )),
        404: openapi.Response(description="Tratamiento no encontrado")
    }
)
@api_view(['POST'])
def cargar_costo(request):
    tratamiento_id = request.data.get('tratamiento')
    try:
        tratamiento = Tratamiento.objects.get(id=tratamiento_id)
        return Response({'costo': tratamiento.precio})
    except Tratamiento.DoesNotExist:
        return Response({'error': 'Tratamiento no encontrado'}, status=404)
    
@swagger_auto_schema(
    method='post',
    operation_summary="Buscar nombre de paciente por ID",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['paciente'],
        properties={
            'paciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del paciente'),
        },
    ),
    responses={
        200: openapi.Response(description="Nombre del paciente", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'nombres': openapi.Schema(type=openapi.TYPE_STRING)}
        )),
        404: openapi.Response(description="Paciente no encontrado")
    }
)
@api_view(['POST'])
def buscar_paciente(request):
    paciente_id = request.data.get('paciente')
    try:
        paciente = Paciente.objects.get(id=paciente_id)
        return Response({'nombres': paciente.name.upper()})
    except Paciente.DoesNotExist:
        return Response({'error': 'Paciente no encontrado'}, status=404)



@swagger_auto_schema(
    method='post',
    operation_summary="Validar documento y correo de paciente",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['numero', 'correo'],
        properties={
            'numero': openapi.Schema(type=openapi.TYPE_STRING, description='Número de documento'),
            'correo': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='Correo electrónico'),
        },
    ),
    responses={
        200: openapi.Response(description="Resultado de validación", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'docu': openapi.Schema(type=openapi.TYPE_STRING, enum=['Si', 'No']),
                'correo': openapi.Schema(type=openapi.TYPE_STRING, enum=['Si', 'No']),
            }
        ))
    }
)
@api_view(['POST'])
def validar_documento(request):
    numero = request.data.get('numero')
    correo = request.data.get('correo')

    docu = 'Si' if Paciente.objects.filter(NumDoc=numero).exists() else 'No'
    email = 'Si' if Paciente.objects.filter(email=correo).exists() else 'No'

    return Response({'docu': docu, 'correo': email})


@swagger_auto_schema(
    method='post',
    operation_summary="Validar si un DNI ya existe en el sistema",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['numero'],
        properties={
            'numero': openapi.Schema(type=openapi.TYPE_STRING, description='Número de documento a validar'),
        },
    ),
    responses={
        200: openapi.Response(description="Resultado de validación", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'datos': openapi.Schema(type=openapi.TYPE_STRING, enum=['Si', 'No']),
            }
        ))
    }
)
@api_view(['POST'])
def validar_dni(request):
    numero = request.data.get('numero')
    existe = 'Si' if User.objects.filter(num_doc=numero).exists() else 'No'
    return Response({'datos': existe})


@swagger_auto_schema(
    method='get',
    operation_summary="Cargar calendario con citas",
    responses={
        200: openapi.Response(description="Lista de eventos de citas", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'datos': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                        'paciente': openapi.Schema(type=openapi.TYPE_STRING),
                        'tratamiento': openapi.Schema(type=openapi.TYPE_STRING),
                        'enfermedad': openapi.Schema(type=openapi.TYPE_STRING),
                        'fecha': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'color': openapi.Schema(type=openapi.TYPE_STRING),
                    })
                )
            }
        ))
    }
)
@api_view(['GET'])
def cargar_calendario(request):
    eventos = []
    citas = Cita.objects.select_related('paciente', 'tratamiento').all()

    for cita in citas:
        paciente = cita.paciente.name.upper()
        tratamiento = cita.tratamiento.tratamiento
        color = '#C92417' if cita.estadoCita == 'Asignado' else '#539B0A'
        eventos.append({
            'paciente': paciente,
            'tratamiento': tratamiento,
            'enfermedad': cita.enfermedad,
            'fecha': f"{cita.fecha} {cita.hora}",
            'color': color,
        })
    return Response({'datos': eventos})


@swagger_auto_schema(
    method='post',
    operation_summary="Buscar paciente por DNI",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['dni'],
        properties={
            'dni': openapi.Schema(type=openapi.TYPE_STRING, description='Número de documento'),
        },
    ),
    responses={
        200: openapi.Response(description="Lista de pacientes", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'datos': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)  # optional: you can pass full serializer schema here
                )
            }
        ))
    }
)
@api_view(['POST'])
def buscar_dni(request):
    dni = request.data.get('dni')
    pacientes = Paciente.objects.filter(num_doc=dni)  # Fix field name if needed
    serializer = PacienteSerializer(pacientes, many=True)
    return Response({'datos': serializer.data})



@swagger_auto_schema(
    method='post',
    operation_summary="Validar rango de horas entre citas de un paciente en la misma fecha",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['idpaciente', 'fecha', 'hora'],
        properties={
            'idpaciente': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del paciente'),
            'fecha': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de la nueva cita (YYYY-MM-DD)'),
            'hora': openapi.Schema(type=openapi.TYPE_STRING, pattern='^\\d{2}:\\d{2}$', description='Hora de la nueva cita (HH:MM)'),
        },
    ),
    responses={
        200: openapi.Response(description="Rango en horas respecto a la última cita registrada ese día", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rango': openapi.Schema(type=openapi.TYPE_INTEGER, description='Diferencia en horas entre citas'),
            }
        )),
    },
    tags=["Citas"]
)
@api_view(['POST'])
def validar_registro(request):
    paciente_id = request.data.get('idpaciente')
    fecha = request.data.get('fecha')
    hora = request.data.get('hora')

    ultima_cita = Cita.objects.filter(paciente_id=paciente_id, fecha=fecha).order_by('-id').first()
    rango = 100

    if ultima_cita:
        from datetime import datetime
        nueva_fecha = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        ultima_fecha = datetime.combine(ultima_cita.fecha, ultima_cita.hora)
        rango = abs(int((nueva_fecha - ultima_fecha).total_seconds() // 3600))

    return Response({'rango': rango})