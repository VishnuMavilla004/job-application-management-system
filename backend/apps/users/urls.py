
from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema

from apps.users.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ProfileView,
)

class PublicTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    @extend_schema(auth=[])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

urlpatterns = [
    path(
    "auth/refresh/",
    PublicTokenRefreshView.as_view(),
    name="token-refresh",
    ),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path(
        "auth/change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "auth/password-reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset",
    ),
    path(
        "auth/password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("users/me/", ProfileView.as_view(), name="user-profile"),
]
