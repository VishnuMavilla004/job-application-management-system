import pytest

from django.urls import reverse
from rest_framework import status

from apps.applications.models import (
    JobApplication,
    ApplicationStatusHistory,
)


pytestmark = pytest.mark.django_db


class TestCompanyAPI:

    def test_authenticated_user_can_list_companies(
        self,
        authenticated_client,
        company,
    ):
        response = authenticated_client.get(
            "/api/v1/companies/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1 if isinstance(
            response.data, dict
        ) and "results" in response.data else len(response.data) >= 1

    def test_authenticated_user_can_create_company(
        self,
        authenticated_client,
    ):
        response = authenticated_client.post(
            "/api/v1/companies/",
            {
                "name": "Microsoft",
                "website": "https://www.microsoft.com",
                "industry": "Technology",
                "location": "Hyderabad",
                "description": "Software company",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_unauthenticated_user_cannot_list_companies(
        self,
        api_client,
    ):
        response = api_client.get("/api/v1/companies/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestApplicationCreateAPI:

    def test_user_can_create_application(
        self,
        authenticated_client,
        company,
        user,
    ):
        response = authenticated_client.post(
            "/api/v1/applications/",
            {
                "company_id": company.id,
                "job_title": "Python Developer",
                "job_description": "Backend developer position.",
                "location": "Bengaluru",
                "employment_type": "full_time",
                "work_mode": "remote",
                "salary_min": 500000,
                "salary_max": 900000,
                "job_url": "https://example.com/jobs/1",
                "status": "applied",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert JobApplication.objects.filter(
            user=user,
            job_title="Python Developer",
        ).exists()

    def test_application_owner_is_assigned_automatically(
        self,
        authenticated_client,
        company,
        user,
    ):
        response = authenticated_client.post(
            "/api/v1/applications/",
            {
                "company_id": company.id,
                "job_title": "Backend Engineer",
                "employment_type": "full_time",
                "work_mode": "hybrid",
                "status": "applied",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        application = JobApplication.objects.get(
            job_title="Backend Engineer"
        )

        assert application.user == user

    def test_user_cannot_assign_application_to_another_user(
        self,
        authenticated_client,
        company,
        another_user,
    ):
        response = authenticated_client.post(
            "/api/v1/applications/",
            {
                "user": another_user.id,
                "company_id": company.id,
                "job_title": "Unauthorized Assignment",
                "employment_type": "full_time",
                "work_mode": "remote",
                "status": "applied",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        application = JobApplication.objects.get(
            job_title="Unauthorized Assignment"
        )

        assert application.user != another_user

    def test_invalid_company_is_rejected(
        self,
        authenticated_client,
    ):
        response = authenticated_client.post(
            "/api/v1/applications/",
            {
                "company_id": 999999,
                "job_title": "Python Developer",
                "employment_type": "full_time",
                "work_mode": "remote",
                "status": "applied",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_salary_range_is_rejected(
        self,
        authenticated_client,
        company,
    ):
        response = authenticated_client.post(
            "/api/v1/applications/",
            {
                "company_id": company.id,
                "job_title": "Python Developer",
                "employment_type": "full_time",
                "work_mode": "remote",
                "salary_min": 1000000,
                "salary_max": 500000,
                "status": "applied",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_status_is_rejected(
        self,
        authenticated_client,
        company,
    ):
        response = authenticated_client.post(
            "/api/v1/applications/",
            {
                "company_id": company.id,
                "job_title": "Python Developer",
                "employment_type": "full_time",
                "work_mode": "remote",
                "status": "unknown_status",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_application_creation_records_initial_status_history(
        self,
        authenticated_client,
        company,
    ):
        response = authenticated_client.post(
            "/api/v1/applications/",
            {
                "company_id": company.id,
                "job_title": "Initial History Test",
                "employment_type": "full_time",
                "work_mode": "remote",
                "status": "applied",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        application = JobApplication.objects.get(
            job_title="Initial History Test"
        )

        assert ApplicationStatusHistory.objects.filter(
            application=application,
            old_status__isnull=True,
            new_status="applied",
        ).exists()


class TestApplicationReadAPI:

    def test_user_can_list_own_applications(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.get(
            "/api/v1/applications/"
        )

        assert response.status_code == status.HTTP_200_OK

    def test_user_can_retrieve_own_application(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.get(
            f"/api/v1/applications/{application.id}/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == application.id

    def test_user_cannot_retrieve_another_users_application(
        self,
        authenticated_client,
        another_user,
        company,
    ):
        other_application = JobApplication.objects.create(
            user=another_user,
            company=company,
            job_title="Private Application",
            employment_type="full_time",
            work_mode="remote",
            status="applied",
        )

        response = authenticated_client.get(
            f"/api/v1/applications/{other_application.id}/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_user_cannot_list_applications(
        self,
        api_client,
    ):
        response = api_client.get(
            "/api/v1/applications/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestApplicationUpdateAPI:

    def test_user_can_update_application(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "job_title": "Senior Python Developer",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        application.refresh_from_db()

        assert application.job_title == "Senior Python Developer"

    def test_status_update_creates_history(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "status": "interview",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        assert ApplicationStatusHistory.objects.filter(
            application=application,
            old_status="applied",
            new_status="interview",
        ).exists()

    def test_non_status_update_does_not_create_extra_history(
        self,
        authenticated_client,
        application,
    ):
        initial_count = ApplicationStatusHistory.objects.filter(
            application=application
        ).count()

        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "job_title": "Updated Title",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        assert ApplicationStatusHistory.objects.filter(
            application=application
        ).count() == initial_count

    def test_user_cannot_update_another_users_application(
        self,
        authenticated_client,
        another_user,
        company,
    ):
        other_application = JobApplication.objects.create(
            user=another_user,
            company=company,
            job_title="Private Application",
            employment_type="full_time",
            work_mode="remote",
            status="applied",
        )

        response = authenticated_client.patch(
            f"/api/v1/applications/{other_application.id}/",
            {
                "job_title": "Unauthorized Update",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestApplicationDeleteAPI:

    def test_user_can_delete_own_application(
        self,
        authenticated_client,
        application,
    ):
        application_id = application.id

        response = authenticated_client.delete(
            f"/api/v1/applications/{application_id}/"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        assert not JobApplication.objects.filter(
            id=application_id
        ).exists()

    def test_user_cannot_delete_another_users_application(
        self,
        authenticated_client,
        another_user,
        company,
    ):
        other_application = JobApplication.objects.create(
            user=another_user,
            company=company,
            job_title="Private Application",
            employment_type="full_time",
            work_mode="remote",
            status="applied",
        )

        response = authenticated_client.delete(
            f"/api/v1/applications/{other_application.id}/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        assert JobApplication.objects.filter(
            id=other_application.id
        ).exists()


class TestApplicationHistoryAPI:

    def test_user_can_view_application_history(
        self,
        authenticated_client,
        application,
    ):
        ApplicationStatusHistory.objects.create(
            application=application,
            old_status=None,
            new_status="applied",
            remarks="Application created.",
        )

        response = authenticated_client.get(
            f"/api/v1/applications/{application.id}/history/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_user_cannot_view_another_users_history(
        self,
        authenticated_client,
        another_user,
        company,
    ):
        other_application = JobApplication.objects.create(
            user=another_user,
            company=company,
            job_title="Private Application",
            employment_type="full_time",
            work_mode="remote",
            status="applied",
        )

        response = authenticated_client.get(
            f"/api/v1/applications/{other_application.id}/history/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND