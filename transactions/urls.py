from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IngresoViewSet,
)


router = DefaultRouter()
router.register(r'ingresos', IngresoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    ]