from django.urls import path
from .views import (
    LoginView,
    ForgotPasswordView,
    VerifyEmailView,
    ResendVerificationEmailView,
    ResetPasswordView,
    RegisterView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/',    LoginView.as_view(),         name='auth-login'),
    path('forgot-password/',  ForgotPasswordView.as_view(),         name='auth-forgot-password'),
    path('email/verify/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='auth-verify-email'),
    path('email/resend/',     ResendVerificationEmailView.as_view(),name='auth-resend-email'),
    path('reset-password/',     ResetPasswordView.as_view(),          name='auth-reset-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]