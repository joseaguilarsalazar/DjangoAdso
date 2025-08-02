from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from ..serializers import UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


User = get_user_model()

class MedicoListAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Listar todos los médicos, url = medico_list/",
        operation_description="Obtiene una lista de todos los usuarios con el rol 'medico'. "
                              "Se puede filtrar por especialidad, nombre y fecha de registro.",
        manual_parameters=[
            openapi.Parameter('especialidad', openapi.IN_QUERY, description="ID de la especialidad", type=openapi.TYPE_INTEGER),
            openapi.Parameter('nombre', openapi.IN_QUERY, description="Nombre del médico (búsqueda parcial)", type=openapi.TYPE_STRING),
            openapi.Parameter('fecha', openapi.IN_QUERY, description="Fecha de registro (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(description="Lista de médicos.", schema=UserSerializer(many=True)),
            204: openapi.Response(description="No hay médicos registrados."),
        }
    )
    def get(self, request):
        lista_medicos = User.objects.filter(rol='medico')

        # ✅ Aplicar filtros
        especialidad = request.GET.get('especialidad')
        nombre = request.GET.get('nombre')
        fecha = request.GET.get('fecha')

        if especialidad:
            lista_medicos = lista_medicos.filter(especialidad__id=especialidad)

        if nombre:
            lista_medicos = lista_medicos.filter(name__icontains=nombre)

        if fecha:
            lista_medicos = lista_medicos.filter(created_at__date=fecha)

        # ✅ Respuesta si no hay resultados
        if not lista_medicos.exists():
            return Response({'Empty': 'No hay médicos registrados'}, status=status.HTTP_204_NO_CONTENT)

        serialized = UserSerializer(lista_medicos, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
