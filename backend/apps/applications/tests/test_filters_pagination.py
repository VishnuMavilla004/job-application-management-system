from datetime import date

import pytest
from rest_framework import status

from apps.applications.models import JobApplication


pytestmark = pytest.mark.django_db



def create_application(
    user,
    company,
    title,
    application_status="applied",
    location="Bengaluru",
    salary_min=500000,
    salary_max=900000,
    applied_date=date(2026, 1, 15),
    employment_type="full_time",
    work_mode="remote",
):
    return JobApplication.objects.create(
        user=user,
        company=company,
        job_title=title,
        location=location,
        employment_type=employment_type,
        work_mode=work_mode,
        salary_min=salary_min,
        salary_max=salary_max,
        status=application_status,
        applied_date=applied_date,
    )


class TestApplicationSearch:

    def test_search_by_job_title(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Python Backend Developer",
        )

        response = authenticated_client.get(
            "/api/v1/applications/?search=Python"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert "Python" in response.data["results"][0]["job_title"]

    def test_search_by_company_name(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Software Engineer",
        )

        response = authenticated_client.get(
            "/api/v1/applications/?search=Google"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_search_is_case_insensitive(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Python Developer",
        )

        response = authenticated_client.get(
            "/api/v1/applications/?search=python"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


class TestApplicationFiltering:

    def test_filter_by_status(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Backend Developer",
            application_status="interview",
        )

        create_application(
            user,
            company,
            "Python Developer",
            application_status="applied",
        )

        response = authenticated_client.get(
            "/api/v1/applications/?status=interview"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["status"] == "interview"

    def test_filter_by_location(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Bengaluru Developer",
            location="Bengaluru",
        )

        create_application(
            user,
            company,
            "Hyderabad Developer",
            location="Hyderabad",
        )

        response = authenticated_client.get(
            "/api/v1/applications/?location=bengaluru"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_by_employment_type(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Full Time Developer",
            employment_type="full_time",
        )

        create_application(
            user,
            company,
            "Intern Developer",
            employment_type="internship",
        )

        response = authenticated_client.get(
            "/api/v1/applications/?employment_type=internship"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_by_work_mode(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Remote Developer",
            work_mode="remote",
        )

        create_application(
            user,
            company,
            "Hybrid Developer",
            work_mode="hybrid",
        )

        response = authenticated_client.get(
            "/api/v1/applications/?work_mode=remote"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_by_company(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Google Developer",
        )

        response = authenticated_client.get(
            f"/api/v1/applications/?company={company.id}"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_by_minimum_salary(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "High Salary Developer",
            salary_min=800000,
            salary_max=1200000,
        )

        create_application(
            user,
            company,
            "Low Salary Developer",
            salary_min=300000,
            salary_max=500000,
        )

        response = authenticated_client.get(
            "/api/v1/applications/?minimum_salary=700000"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_by_maximum_salary(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Affordable Developer",
            salary_min=400000,
            salary_max=600000,
        )

        create_application(
            user,
            company,
            "Expensive Developer",
            salary_min=1000000,
            salary_max=1500000,
        )

        response = authenticated_client.get(
            "/api/v1/applications/?maximum_salary=700000"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_by_applied_date_range(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "January Application",
            applied_date=date(2026, 1, 10),
        )

        create_application(
            user,
            company,
            "March Application",
            applied_date=date(2026, 3, 10),
        )

        response = authenticated_client.get(
            "/api/v1/applications/"
            "?applied_after=2026-02-01"
            "&applied_before=2026-04-01"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["job_title"] == (
            "March Application"
        )

    def test_multiple_filters_can_be_combined(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Matching Interview",
            application_status="interview",
            location="Bengaluru",
        )

        create_application(
            user,
            company,
            "Rejected Application",
            application_status="rejected",
            location="Bengaluru",
        )

        create_application(
            user,
            company,
            "Remote Interview",
            application_status="interview",
            location="Hyderabad",
        )

        response = authenticated_client.get(
            "/api/v1/applications/"
            "?status=interview&location=Bengaluru"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["job_title"] == (
            "Matching Interview"
        )

    def test_invalid_date_filter_returns_validation_error(
        self,
        authenticated_client,
    ):
        response = authenticated_client.get(
            "/api/v1/applications/?applied_after=not-a-date"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestApplicationOrdering:

    def test_order_by_applied_date_ascending(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Later Application",
            applied_date=date(2026, 5, 1),
        )

        create_application(
            user,
            company,
            "Earlier Application",
            applied_date=date(2026, 2, 1),
        )

        response = authenticated_client.get(
            "/api/v1/applications/?ordering=applied_date"
        )

        assert response.status_code == status.HTTP_200_OK

        titles = [
            item["job_title"]
            for item in response.data["results"]
        ]

        assert titles.index("Earlier Application") < titles.index(
            "Later Application"
        )

    def test_order_by_applied_date_descending(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Earlier Application",
            applied_date=date(2026, 2, 1),
        )

        create_application(
            user,
            company,
            "Later Application",
            applied_date=date(2026, 5, 1),
        )

        response = authenticated_client.get(
            "/api/v1/applications/?ordering=-applied_date"
        )

        assert response.status_code == status.HTTP_200_OK

        titles = [
            item["job_title"]
            for item in response.data["results"]
        ]

        assert titles.index("Later Application") < titles.index(
            "Earlier Application"
        )

    def test_invalid_ordering_field_is_ignored(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_application(
            user,
            company,
            "Python Developer",
        )

        response = authenticated_client.get(
            "/api/v1/applications/?ordering=password"
        )

        assert response.status_code == status.HTTP_200_OK


class TestApplicationPagination:

    def test_default_page_size_is_ten(
        self,
        authenticated_client,
        user,
        company,
    ):
        for number in range(12):
            create_application(
                user,
                company,
                f"Developer {number}",
            )

        response = authenticated_client.get(
            "/api/v1/applications/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 12
        assert len(response.data["results"]) == 10
        assert response.data["next"] is not None

    def test_custom_page_size(
        self,
        authenticated_client,
        user,
        company,
    ):
        for number in range(12):
            create_application(
                user,
                company,
                f"Developer {number}",
            )

        response = authenticated_client.get(
            "/api/v1/applications/?page_size=5"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 12
        assert len(response.data["results"]) == 5

    def test_second_page(
        self,
        authenticated_client,
        user,
        company,
    ):
        for number in range(12):
            create_application(
                user,
                company,
                f"Developer {number}",
            )

        response = authenticated_client.get(
            "/api/v1/applications/?page=2&page_size=5"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 5
        assert response.data["previous"] is not None

    def test_page_size_cannot_exceed_maximum(
        self,
        authenticated_client,
        user,
        company,
    ):
        for number in range(12):
            create_application(
                user,
                company,
                f"Developer {number}",
            )

        response = authenticated_client.get(
            "/api/v1/applications/?page_size=500"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 12

    def test_pagination_does_not_expose_other_users_applications(
        self,
        authenticated_client,
        another_user,
        company,
    ):
        for number in range(3):
            create_application(
                another_user,
                company,
                f"Other User Application {number}",
            )

        response = authenticated_client.get(
            "/api/v1/applications/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0