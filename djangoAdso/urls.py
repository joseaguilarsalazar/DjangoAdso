"""
URL configuration for djangoAdso project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static
from django.conf import settings


# ✅ Swagger schema configuration
schema_view = get_schema_view(
   openapi.Info(
      title="ADSO API",
      default_version="v0.1",
      description="API for managing adso operations",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="admin@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin (opcional)
    path('admin/', admin.site.urls),

    # Tu API
    path('api/', include('core.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('odontograma.urls')),
    path('api/', include('transactions.urls')),

    # ✅ Swagger and Redoc URLs<
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Sirve archivos MEDIA en desarrollo
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)