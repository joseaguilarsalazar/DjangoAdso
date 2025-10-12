from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IngresoViewSet,
    CierreDeCajaApiView,
)


router = DefaultRouter()
router.register(r'ingresos', IngresoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cierre-de-caja/', CierreDeCajaApiView.as_view(), name='cierre-de-caja'),
    ]