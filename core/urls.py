from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet, basename='paciente')
router.register(r'tratamientos', TratamientoViewSet)
router.register(r'especialidades', EspecialidadViewSet)
router.register(r'citas', CitaViewSet, basename='cita')
router.register(r'clinicas', ClinicaViewSet)
router.register(r'alergias', AlergiaViewSet)
router.register(r'paciente_alergias', PacienteAlergiaViewSet)
router.register(r'bancos', BancoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'enfermedades', EnfermedadViewSet)
router.register(r'paciente_evoluciones', PacienteEvolucionViewSet)
router.register(r'paciente_enfermedades', PacienteEnfermedadViewSet)
router.register(r'paciente_diagnosticos', PacienteDiagnosticoViewSet)
router.register(r'paciente_placas', PacientePlacaViewSet)
router.register(r'users', UserViewset)
router.register(r'consultorios', ConsultorioViewSet)
router.register(r'categoria_tratamiento', CategoriaTratamientoViewSet)
router.register(r'tratamiento_paciente', TratamientoPacienteViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('cargar-costo/', cargar_costo),
    path('buscar-paciente/', buscar_paciente),
    path('validar-documento/', validar_documento),
    path('validar-dni/', validar_dni),
    path('calendario/', cargar_calendario),
    path('uscar-dni/', buscar_dni),
    path('validar-registro/', validar_registro),
    path('envio_mensaje_test/', EnvioMensajeAPIView.as_view()),
    path('medico_list/', MedicoListAPIView.as_view()),
    path('historial/', HistorialApiView.as_view()),
    path('agenda_today/', TodayScheduleApi.as_view()),
    path('citas_histograma/', CitasHistogramaApiView.as_view()),
    path('ingresos_egresos_histograma/', IngresosEgresosHistogramaApiView.as_view()),
    path('tratamiento-statistics/', TratamientoStatisticsApiView.as_view()),
    path('recent-patients/', RecentPatientsCountView.as_view()),
    path('trigger-survey-broadcast/', TriggerSurveyBroadcastView.as_view()),
    path('encuesta-status/', EncuestaStatusView.as_view()),
]
