from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PagosViewSet,
)


router = DefaultRouter()
router.register(r'pacientes', PagosViewSet)

urlpatterns = [
    path('', include(router.urls)),
    ]