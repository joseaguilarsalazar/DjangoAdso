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
    PacientePlacaViewSet, ConsultorioViewSet, CategoriaTratamientoViewSet,
    TratamientoPacienteViewSet,
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
from .todayScheduleApi import TodayScheduleApi
from .statisticsViews import (
    CitasHistogramaApiView,
    IngresosEgresosHistogramaApiView,
)
from EncuestaView import TriggerSurveyBroadcastView
from recent_patients import RecentPatientsCountView

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
    "ConsultorioViewSet",
    "EspecialidadViewSet",
    "PacientePlacaViewSet",
    "PacienteAlergiaViewSet",
    "PacienteEvolucionViewSet",
    "PacienteEnfermedadViewSet",
    "PacienteDiagnosticoViewSet",
    "TratamientoPacienteViewSet",
    "CategoriaTratamientoViewSet",
    

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
    "TodayScheduleApi",
    "RecentPatientsCountView",
    "TriggerSurveyBroadcastView",

    # statisticsViews
    "CitasHistogramaApiView",
    "IngresosEgresosHistogramaApiView",
]
