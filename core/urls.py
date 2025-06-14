from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'historiales', HistorialViewSet)
router.register(r'tratamientos', TratamientoViewSet)
router.register(r'especialidades', EspecialidadViewSet)
router.register(r'citas', CitaViewSet)
router.register(r'pagos', PagosViewSet)
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
]
