from .coreViewsets import (
    CitaViewSet,
    UserViewset,
    AlergiaViewSet,
    ClinicaViewSet,
    PacienteViewSet,
    CategoriaViewSet,
    EnfermedadViewSet,
    TratamientoViewSet,
    EspecialidadViewSet,
    PacienteAlergiaViewSet,
    PacienteEvolucionViewSet,
    PacienteEnfermedadViewSet,
    BancoViewSet,
    PacienteDiagnosticoViewSet,
    PacientePlacaViewSet,
)
from .predoneViews import (
    validar_dni,
    validar_documento,
    validar_registro,
    cargar_calendario,
    cargar_costo,
    buscar_dni,
    buscar_paciente,
)
from .EnvioMensajeAPIView import EnvioMensajeAPIView
from .MedicosListView import MedicoListAPIView
from .HistorialApiView import HistorialApiView

__all__ = [
    # coreViewsets
    "CitaViewSet",
    "UserViewset",
    "BancoViewSet",
    "AlergiaViewSet",
    "ClinicaViewSet",
    "PacienteViewSet",
    "CategoriaViewSet",
    "EnfermedadViewSet",
    "TratamientoViewSet",
    "EspecialidadViewSet",
    "PacientePlacaViewSet",
    "PacienteAlergiaViewSet",
    "PacienteEvolucionViewSet",
    "PacienteEnfermedadViewSet",
    "PacienteDiagnosticoViewSet",

    # predoneViews
    "validar_dni",
    "validar_documento",
    "validar_registro",
    "cargar_calendario",
    "cargar_costo",
    "buscar_dni",
    "buscar_paciente",

    #other views
    "EnvioMensajeAPIView",
    'MedicoListAPIView',
    "HistorialApiView",
]
