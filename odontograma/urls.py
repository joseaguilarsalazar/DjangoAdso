from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DienteViewSet,
    OdontogramaViewSet,
    CasoMultidentalViewSet,
    HallazgoViewSet
)

router = DefaultRouter()
router.register(r'dientes', DienteViewSet)
router.register(r'odontogramas', OdontogramaViewSet)
router.register(r'casos_multidental', CasoMultidentalViewSet)
router.register(r'hallazgos', HallazgoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]