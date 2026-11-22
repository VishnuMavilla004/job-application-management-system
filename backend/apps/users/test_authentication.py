import re
from urllib.parse import urlparse, parse_qs

import pytest

from django.contrib.auth import get_user_model
from django.core import mail

from rest_framework.test import APIClient


User = get_user_model()

PASSWORD = "N0tCommon!Pass_928"


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="rahul@example.com",
        password=PASSWORD,
        first_name="Rahul",
        last_name="Kumar",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    response = api_client.post(
        "/api/v1/auth/login/",
        {
            "email": user.email,
            "password": PASSWORD,
        },
        format="json",
    )

    assert response.status_code == 200, response.data

    access = response.data["data"]["tokens"]["access"]

    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )

    return api_client


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRegistration:

    def test_successful_registration(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": PASSWORD,
                "password_confirm": PASSWORD,
            },
            format="json",
        )

        assert response.status_code == 201, response.data
        assert response.data["success"] is True

        assert User.objects.filter(
            email="newuser@example.com"
        ).exists()

        assert "access" in response.data["data"]["tokens"]
        assert "refresh" in response.data["data"]["tokens"]

        created_user = User.objects.get(
            email="newuser@example.com"
        )
        assert created_user.check_password(PASSWORD)

    def test_duplicate_email_rejected(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": user.email,
                "first_name": "Duplicate",
                "password": PASSWORD,
                "password_confirm": PASSWORD,
            },
            format="json",
        )

        assert response.status_code == 400

    def test_password_mismatch(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "mismatch@example.com",
                "first_name": "Mismatch",
                "password": PASSWORD,
                "password_confirm": "DifferentPass123!",
            },
            format="json",
        )

        assert response.status_code == 400

    def test_weak_password_rejected(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "weak@example.com",
                "first_name": "Weak",
                "password": "12345678",
                "password_confirm": "12345678",
            },
            format="json",
        )

        assert response.status_code == 400

    def test_registration_requires_email(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Missing",
                "password": PASSWORD,
                "password_confirm": PASSWORD,
            },
            format="json",
        )

        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestLogin:

    def test_successful_login(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": PASSWORD,
            },
            format="json",
        )

        assert response.status_code == 200, response.data
        assert response.data["success"] is True
        assert "access" in response.data["data"]["tokens"]
        assert "refresh" in response.data["data"]["tokens"]

    def test_invalid_password(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": "WrongPassword123!",
            },
            format="json",
        )

        assert response.status_code == 400

    def test_nonexistent_user(self, api_client):
        response = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": "unknown@example.com",
                "password": PASSWORD,
            },
            format="json",
        )

        assert response.status_code == 400

    def test_inactive_user_cannot_login(self, api_client, user):
        user.is_active = False
        user.save(update_fields=["is_active"])

        response = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": PASSWORD,
            },
            format="json",
        )

        assert response.status_code == 400


# ---------------------------------------------------------------------------
# JWT and logout
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestJWT:

    def test_protected_endpoint_requires_token(self, api_client):
        response = api_client.get(
            "/api/v1/users/me/"
        )

        assert response.status_code == 401

    def test_valid_access_token(self, authenticated_client):
        response = authenticated_client.get(
            "/api/v1/users/me/"
        )

        assert response.status_code == 200

    def test_token_refresh(self, api_client, user):
        login = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": PASSWORD,
            },
            format="json",
        )

        assert login.status_code == 200, login.data
        refresh = login.data["data"]["tokens"]["refresh"]

        response = api_client.post(
            "/api/v1/auth/refresh/",
            {"refresh": refresh},
            format="json",
        )

        assert response.status_code == 200, response.data
        assert "access" in response.data

    def test_logout_blacklists_refresh_token(self, api_client, user):
        login = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": PASSWORD,
            },
            format="json",
        )

        assert login.status_code == 200, login.data
        tokens = login.data["data"]["tokens"]

        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}"
        )

        logout = api_client.post(
            "/api/v1/auth/logout/",
            {"refresh": tokens["refresh"]},
            format="json",
        )

        assert logout.status_code == 200, logout.data

        api_client.credentials()

        refresh_response = api_client.post(
            "/api/v1/auth/refresh/",
            {"refresh": tokens["refresh"]},
            format="json",
        )

        assert refresh_response.status_code == 401

    def test_user_cannot_logout_another_users_token(
        self,
        api_client,
        user,
        db,
    ):
        another_user = User.objects.create_user(
            email="another@example.com",
            password=PASSWORD,
            first_name="Another",
        )

        login_one = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": PASSWORD,
            },
            format="json",
        )

        login_two = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": another_user.email,
                "password": PASSWORD,
            },
            format="json",
        )

        assert login_one.status_code == 200, login_one.data
        assert login_two.status_code == 200, login_two.data

        api_client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {login_one.data['data']['tokens']['access']}"
            )
        )

        response = api_client.post(
            "/api/v1/auth/logout/",
            {
                "refresh": (
                    login_two.data["data"]["tokens"]["refresh"]
                )
            },
            format="json",
        )

        assert response.status_code in (400, 403)

        # The second user's refresh token must remain usable.
        api_client.credentials()

        refresh_response = api_client.post(
            "/api/v1/auth/refresh/",
            {
                "refresh": login_two.data["data"]["tokens"]["refresh"]
            },
            format="json",
        )

        assert refresh_response.status_code == 200


# ---------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProfile:

    def test_get_profile(self, authenticated_client, user):
        response = authenticated_client.get(
            "/api/v1/users/me/"
        )

        assert response.status_code == 200, response.data
        assert response.data["data"]["email"] == user.email

    def test_update_profile(self, authenticated_client, user):
        response = authenticated_client.patch(
            "/api/v1/users/me/",
            {
                "first_name": "Updated",
                "last_name": "Developer",
                "phone_number": "9876543210",
            },
            format="json",
        )

        assert response.status_code == 200, response.data

        user.refresh_from_db()

        assert user.first_name == "Updated"
        assert user.last_name == "Developer"
        assert user.phone_number == "9876543210"

    def test_email_cannot_be_changed_through_profile(
        self,
        authenticated_client,
        user,
    ):
        response = authenticated_client.patch(
            "/api/v1/users/me/",
            {
                "email": "attacker@example.com",
            },
            format="json",
        )

        assert response.status_code == 200, response.data

        user.refresh_from_db()
        assert user.email == "rahul@example.com"


# ---------------------------------------------------------------------------
# Password change
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPasswordChange:

    def test_successful_password_change(
        self,
        authenticated_client,
        user,
    ):
        response = authenticated_client.post(
            "/api/v1/auth/change-password/",
            {
                "old_password": PASSWORD,
                "new_password": "Another!SecurePass928",
                "confirm_password": "Another!SecurePass928",
            },
            format="json",
        )

        assert response.status_code == 200, response.data

        user.refresh_from_db()
        assert user.check_password("Another!SecurePass928")

    def test_wrong_old_password(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/auth/change-password/",
            {
                "old_password": "WrongPassword123!",
                "new_password": "Another!SecurePass928",
                "confirm_password": "Another!SecurePass928",
            },
            format="json",
        )

        assert response.status_code == 400

    def test_password_confirmation_mismatch(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/auth/change-password/",
            {
                "old_password": PASSWORD,
                "new_password": "Another!SecurePass928",
                "confirm_password": "Different!Password928",
            },
            format="json",
        )

        assert response.status_code == 400

    def test_new_password_is_different(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/auth/change-password/",
            {
                "old_password": PASSWORD,
                "new_password": PASSWORD,
                "confirm_password": PASSWORD,
            },
            format="json",
        )

        assert response.status_code == 400

    def test_password_change_revokes_refresh_tokens(
        self,
        api_client,
        user,
    ):
        login = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": PASSWORD,
            },
            format="json",
        )

        assert login.status_code == 200, login.data
        tokens = login.data["data"]["tokens"]

        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}"
        )

        response = api_client.post(
            "/api/v1/auth/change-password/",
            {
                "old_password": PASSWORD,
                "new_password": "Another!SecurePass928",
                "confirm_password": "Another!SecurePass928",
            },
            format="json",
        )

        assert response.status_code == 200, response.data

        api_client.credentials()

        refresh_response = api_client.post(
            "/api/v1/auth/refresh/",
            {"refresh": tokens["refresh"]},
            format="json",
        )

        assert refresh_response.status_code == 401


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPasswordReset:

    @pytest.fixture(autouse=True)
    def configure_email_backend(self, settings):
        """
        Use Django's in-memory email backend for every password-reset test.
        This is a pytest fixture, not Django's override_settings class
        decorator, so it works with a pytest test class.
        """
        settings.EMAIL_BACKEND = (
            "django.core.mail.backends.locmem.EmailBackend"
        )
        mail.outbox = []

    def test_password_reset_request(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/password-reset/",
            {"email": user.email},
            format="json",
        )

        assert response.status_code == 200, response.data
        assert len(mail.outbox) == 1
        assert user.email in mail.outbox[0].to

    def test_unknown_email_returns_same_message(self, api_client):
        response = api_client.post(
            "/api/v1/auth/password-reset/",
            {"email": "unknown@example.com"},
            format="json",
        )

        assert response.status_code == 200, response.data
        assert len(mail.outbox) == 0
        assert "account exists" in response.data["message"].lower()

    def test_successful_password_reset(self, api_client, user):
        request_response = api_client.post(
            "/api/v1/auth/password-reset/",
            {"email": user.email},
            format="json",
        )

        assert request_response.status_code == 200, request_response.data
        assert len(mail.outbox) == 1

        email_body = mail.outbox[0].body

        url_match = re.search(
            r"http://localhost:5173/reset-password\?[^\s]+",
            email_body,
        )
        assert url_match is not None

        reset_url = url_match.group(0).rstrip(".,)")
        parsed = urlparse(reset_url)
        params = parse_qs(parsed.query)

        assert "uid" in params
        assert "token" in params

        response = api_client.post(
            "/api/v1/auth/password-reset/confirm/",
            {
                "uid": params["uid"][0],
                "token": params["token"][0],
                "new_password": "Reset!SecurePassword928",
                "confirm_password": "Reset!SecurePassword928",
            },
            format="json",
        )

        assert response.status_code == 200, response.data

        user.refresh_from_db()
        assert user.check_password("Reset!SecurePassword928")

    def test_invalid_reset_token(self, api_client, user):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        response = api_client.post(
            "/api/v1/auth/password-reset/confirm/",
            {
                "uid": uid,
                "token": "invalid-token",
                "new_password": "Reset!SecurePassword928",
                "confirm_password": "Reset!SecurePassword928",
            },
            format="json",
        )

        assert response.status_code == 400

    def test_password_reset_revokes_refresh_tokens(
        self,
        api_client,
        user,
    ):
        login = api_client.post(
            "/api/v1/auth/login/",
            {
                "email": user.email,
                "password": PASSWORD,
            },
            format="json",
        )

        assert login.status_code == 200, login.data
        old_refresh = login.data["data"]["tokens"]["refresh"]

        reset_response = api_client.post(
            "/api/v1/auth/password-reset/",
            {"email": user.email},
            format="json",
        )

        assert reset_response.status_code == 200, reset_response.data
        assert len(mail.outbox) == 1

        email_body = mail.outbox[0].body

        url_match = re.search(
            r"http://localhost:5173/reset-password\?[^\s]+",
            email_body,
        )
        assert url_match is not None

        reset_url = url_match.group(0).rstrip(".,)")
        parsed = urlparse(reset_url)
        params = parse_qs(parsed.query)

        assert "uid" in params
        assert "token" in params

        response = api_client.post(
            "/api/v1/auth/password-reset/confirm/",
            {
                "uid": params["uid"][0],
                "token": params["token"][0],
                "new_password": "Reset!SecurePassword928",
                "confirm_password": "Reset!SecurePassword928",
            },
            format="json",
        )

        assert response.status_code == 200, response.data

        user.refresh_from_db()
        assert user.check_password("Reset!SecurePassword928")

        refresh_response = api_client.post(
            "/api/v1/auth/refresh/",
            {"refresh": old_refresh},
            format="json",
        )

        assert refresh_response.status_code == 401
