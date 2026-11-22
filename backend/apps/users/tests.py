from django.test import Client, TestCase

from django.contrib.auth import get_user_model

User = get_user_model()


class TestUserModel(TestCase):

    def test_create_user(self):

        user = User.objects.create_user(
            email="rahul@example.com",
            password="SecurePass123!",
            first_name="Rahul",
        )

        assert user.email.split("@")[1] == "example.com"
        assert user.first_name == "Rahul"
        assert user.is_active is True
        assert user.is_staff is False

    def test_password_is_hashed(self):

        password = "SecurePass123!"

        user = User.objects.create_user(
            email="test@example.com",
            password=password,
            first_name="Test",
        )

        assert user.password != password
        assert user.check_password(password)

    def test_email_normalization(self):

        user = User.objects.create_user(
            email="TEST@EXAMPLE.COM",
            password="SecurePass123!",
            first_name="Test",
        )

        assert user.email == "test@example.com"

    def test_create_superuser(self):

        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPass123!",
            first_name="Admin",
        )

        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_active is True


class TestHealthAPI(TestCase):

    def test_health_endpoint(self):

        client = Client()

        response = client.get("/api/health/")

        assert response.status_code == 200
        assert response.json()["status"] == "success"