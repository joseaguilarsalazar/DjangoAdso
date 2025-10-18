from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IngresoViewSet,
    CierreDeCajaApiView,
    DeudaPacienteApiView,
)


router = DefaultRouter()
router.register(r'ingresos', IngresoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cierre-de-caja/', CierreDeCajaApiView.as_view(), name='cierre-de-caja'),
    path('deuda-paciente/<int:paciente_id>/', DeudaPacienteApiView.as_view(), name='deuda-paciente'),
    ]