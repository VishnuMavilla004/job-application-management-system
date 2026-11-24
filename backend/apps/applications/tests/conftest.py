
import pytest
from rest_framework.test import APIClient

from apps.users.models import User
from apps.companies.models import Company
from apps.applications.models import JobApplication


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="developer@example.com",
        password="N0tCommon!Pass_928",
        first_name="Developer",
        last_name="Test",
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="another@example.com",
        password="N0tCommon!Pass_928",
        first_name="Another",
        last_name="User",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def company(db):
    return Company.objects.create(
        name="Google",
        website="https://www.google.com",
        industry="Technology",
        location="Bengaluru",
    )


@pytest.fixture
def application(user, company):
    return JobApplication.objects.create(
        user=user,
        company=company,
        job_title="Python Backend Developer",
        job_description="Backend development role.",
        location="Bengaluru",
        employment_type="full_time",
        work_mode="hybrid",
        salary_min=600000,
        salary_max=1000000,
        job_url="https://example.com/jobs/123",
        status="applied",
    )
