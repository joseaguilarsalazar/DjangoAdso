from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DienteViewSet,
    OdontogramaViewSet,
    CasoMultidentalViewSet,
    DienteOdontogramaViewSet,
)

router = DefaultRouter()
router.register(r'dientes', DienteViewSet)
router.register(r'odontogramas', OdontogramaViewSet)
router.register(r'casos_multidental', CasoMultidentalViewSet)
router.register(r'diente_odontograma', DienteOdontogramaViewSet)


urlpatterns = [
    path('', include(router.urls)),
]