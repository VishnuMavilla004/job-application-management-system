
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "profile_picture",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "email",
            "date_joined",
        )


class RegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    password_confirm = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "password_confirm",
        )

    def validate_email(self, value):

        value = User.objects.normalize_email(value)

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })

        try:
            validate_password(
                attrs["password"]
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError({
                "password": list(exc.messages)
            })

        return attrs

    def create(self, validated_data):

        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        return User.objects.create_user(
            password=password,
            **validated_data,
        )


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):

        request = self.context.get("request")

        user = authenticate(
            request=request,
            email=attrs["email"],
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "This account is inactive."}
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_old_password(self, value):

        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Current password is incorrect."
            )

        return value

    def validate(self, attrs):

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError({
                "new_password": "New password must be different."
            })

        try:
            validate_password(
                attrs["new_password"],
                user=self.context["request"].user,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError({
                "new_password": list(exc.messages)
            })

        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):

    uid = serializers.CharField()

    token = serializers.CharField()

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        try:
            validate_password(attrs["new_password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({
                "new_password": list(exc.messages)
            })

        return attrs
