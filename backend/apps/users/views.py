
import logging

from drf_spectacular.utils import extend_schema
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import (
    BlacklistedToken,
    OutstandingToken,
    RefreshToken,
)

from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegistrationSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)

User = get_user_model()

token_generator = PasswordResetTokenGenerator()


def revoke_user_refresh_tokens(user):

    outstanding_tokens = OutstandingToken.objects.filter(
        user=user
    )

    for outstanding in outstanding_tokens:

        try:
            BlacklistedToken.objects.get_or_create(
                token=outstanding
            )
        except Exception:
            logger.exception(
                "Failed to blacklist refresh token for user %s",
                user.pk,
            )
            raise


@extend_schema(
    auth=[],
    description="Public endpoint for user registration.",)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

        logger.info("New user registered: %s", user.email)

        return Response(
            {
                "success": True,
                "message": "Registration successful.",
                "data": {
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )
    
@extend_schema(
    auth=[],
    description="Public endpoint for user login.",)

class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        tokens = serializer.validated_data["tokens"]

        logger.info(
            "User logged in: %s",
            user.email,
        )

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "data": {
                    "user": UserSerializer(user).data,
                    "tokens": tokens,
                },
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(auth=[])
    def post(self, request):

        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        logger.info(
            "User logged in: %s",
            user.email,
        )

        return Response({
            "success": True,
            "message": "Login successful.",
            "data": {
                "user": UserSerializer(user).data,
                "tokens": serializer.validated_data["tokens"],
            },
        })


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token is required.",
                    "errors": {
                        "refresh": ["This field is required."]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            token = RefreshToken(refresh_token)

            if str(token["user_id"]) != str(request.user.pk):
                return Response(
                    {
                        "success": False,
                        "message": "Invalid refresh token.",
                        "errors": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token.blacklist()

        except TokenError:

            return Response(
                {
                    "success": False,
                    "message": "Invalid or expired refresh token.",
                    "errors": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            "User logged out: %s",
            request.user.email,
        )

        return Response(
            {
                "success": True,
                "message": "Logout successful.",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        with transaction.atomic():

            request.user.set_password(
                serializer.validated_data["new_password"]
            )

            request.user.save(
                update_fields=["password"]
            )

            revoke_user_refresh_tokens(request.user)

        logger.info(
            "Password changed for user: %s",
            request.user.email,
        )

        return Response({
            "success": True,
            "message": (
                "Password changed successfully. "
                "Please log in again."
            ),
            "data": None,
        })


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(auth=[])
    def post(self, request):

        serializer = PasswordResetRequestSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = User.objects.filter(
            email__iexact=email,
            is_active=True,
        ).first()

        if user:

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = token_generator.make_token(user)

            frontend_url = getattr(
                settings,
                "FRONTEND_PASSWORD_RESET_URL",
                "http://localhost:5173/reset-password",
            )

            reset_link = (
                f"{frontend_url}?uid={uid}&token={token}"
            )

            send_mail(
                subject="Reset your Job Management account password",

                message=(
                    "We received a password reset request.\n\n"
                    f"Reset your password using this link:\n"
                    f"{reset_link}\n\n"
                    "If you did not request this, ignore this email."
                ),

                from_email=settings.DEFAULT_FROM_EMAIL,

                recipient_list=[user.email],

                fail_silently=False,
            )

            logger.info(
                "Password reset requested for user: %s",
                user.email,
            )

        return Response({
            "success": True,
            "message": (
                "If an account exists with this email, "
                "password reset instructions have been sent."
            ),
            "data": None,
        })


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(auth=[])
    def post(self, request):

        serializer = PasswordResetConfirmSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:

            uid = force_str(
                urlsafe_base64_decode(
                    serializer.validated_data["uid"]
                )
            )

            user = User.objects.get(
                pk=uid,
                is_active=True,
            )

        except (ValueError, TypeError, OverflowError, User.DoesNotExist):

            return Response(
                {
                    "success": False,
                    "message": "Invalid or expired reset link.",
                    "errors": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not token_generator.check_token(
            user,
            serializer.validated_data["token"],
        ):

            return Response(
                {
                    "success": False,
                    "message": "Invalid or expired reset link.",
                    "errors": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():

            user.set_password(
                serializer.validated_data["new_password"]
            )

            user.save(
                update_fields=["password"]
            )

            revoke_user_refresh_tokens(user)

        logger.info(
            "Password reset completed for user: %s",
            user.email,
        )

        return Response({
            "success": True,
            "message": "Password reset successfully.",
            "data": None,
        })


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserSerializer(request.user)

        return Response({
            "success": True,
            "message": "Profile retrieved successfully.",
            "data": serializer.data,
        })

    def patch(self, request):

        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({
            "success": True,
            "message": "Profile updated successfully.",
            "data": serializer.data,
        })
