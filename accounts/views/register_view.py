from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from ..serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=RegisterSerializer
            ),
            400: "Bad Request - invalid input",
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Register a new user.
        """
        return super().post(request, *args, **kwargs)