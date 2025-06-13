from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


# Throttle scope 'verification' → 6 requests / 1 minute
class VerificationThrottle(UserRateThrottle):
    scope = 'verification'


class VerifyEmailView(APIView):
    """
    GET /api/auth/email/verify/<uidb64>/<token>/
    Requiere estar autenticado y un URL firmado.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [VerificationThrottle]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except Exception:
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=['is_active'])
            return Response(
                {"detail": "Email verificado con éxito."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Enlace de verificación inválido o expirado."},
            status=status.HTTP_400_BAD_REQUEST
        )


class ResendVerificationEmailView(APIView):
    """
    POST /api/auth/email/resend/
    Requiere estar autenticado.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [VerificationThrottle]

    def post(self, request):
        user = request.user
        if user.is_active:
            return Response(
                {"detail": "El email ya está verificado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        current_site = get_current_site(request)
        verify_path = f"/api/auth/email/verify/{uidb64}/{token}/"
        verification_url = f"{request.scheme}://{current_site.domain}{verify_path}"

        # Asume que tienes plantillas en <project_root>/templates/auth/
        subject = "Verificación de correo"
        message = render_to_string(
            "auth/email_verification_email.html",
            {"user": user, "verification_url": verification_url}
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Se ha reenviado el enlace de verificación al correo."},
            status=status.HTTP_200_OK
        )