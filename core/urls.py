from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'tratamientos', TratamientoViewSet)
router.register(r'especialidades', EspecialidadViewSet)
router.register(r'citas', CitaViewSet)
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
]
