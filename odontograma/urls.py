from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DienteViewSet,
    OdontogramaViewSet,
    CasoMultidentalViewSet,
    DienteOdontogramaViewSet,
)

router = DefaultRouter()
router.register(r'pacientes', DienteViewSet)
router.register(r'pacientes', OdontogramaViewSet)
router.register(r'pacientes', CasoMultidentalViewSet)
router.register(r'pacientes', DienteOdontogramaViewSet)


urlpatterns = [
    path('', include(router.urls)),
]