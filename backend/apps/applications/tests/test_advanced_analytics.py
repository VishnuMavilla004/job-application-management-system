from datetime import timedelta

import pytest

from django.utils import timezone
from rest_framework import status

from apps.applications.models import (
    ApplicationStatusHistory,
    JobApplication,
)


pytestmark = pytest.mark.django_db


def create_analytics_application(
    user,
    company,
    title,
    application_status="applied",
    applied_date=None,
):
    return JobApplication.objects.create(
        user=user,
        company=company,
        job_title=title,
        location="Bengaluru",
        employment_type="full_time",
        work_mode="hybrid",
        status=application_status,
        applied_date=applied_date or timezone.localdate(),
    )


class TestAdvancedAnalyticsAPI:

    def test_analytics_returns_expected_sections(
        self, authenticated_client
    ):
        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/"
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.data["data"]

        assert "overview" in data
        assert "funnel" in data
        assert "trends" in data
        assert "company_analytics" in data
        assert "status_distribution" in data
        assert "employment_type_distribution" in data

    def test_analytics_uses_requested_date_range(
        self, authenticated_client, user, company
    ):
        today = timezone.localdate()

        create_analytics_application(
            user,
            company,
            "Inside Range",
            applied_date=today - timedelta(days=5),
        )

        create_analytics_application(
            user,
            company,
            "Outside Range",
            applied_date=today - timedelta(days=60),
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/",
            {
                "start_date": (today - timedelta(days=10)).isoformat(),
                "end_date": today.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["overview"]["total_applications"] == 1

    def test_analytics_funnel_uses_status_history(
        self, authenticated_client, user, company
    ):
        application = create_analytics_application(
            user,
            company,
            "Funnel Developer",
            application_status="offer",
        )

        ApplicationStatusHistory.objects.create(
            application=application,
            old_status="applied",
            new_status="assessment",
            changed_by=user,
        )

        ApplicationStatusHistory.objects.create(
            application=application,
            old_status="assessment",
            new_status="interview",
            changed_by=user,
        )

        ApplicationStatusHistory.objects.create(
            application=application,
            old_status="interview",
            new_status="offer",
            changed_by=user,
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/"
        )

        assert response.status_code == status.HTTP_200_OK

        funnel = {
            item["stage"]: item["count"]
            for item in response.data["data"]["funnel"]
        }

        assert funnel["applied"] == 1
        assert funnel["assessment"] == 1
        assert funnel["interview"] == 1
        assert funnel["offer"] == 1

    def test_funnel_does_not_include_other_users_applications(
        self, authenticated_client, another_user, company
    ):
        create_analytics_application(
            another_user,
            company,
            "Other User Application",
            application_status="offer",
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/"
        )

        assert response.status_code == status.HTTP_200_OK

        assert (
            response.data["data"]["overview"]["total_applications"]
            == 0
        )

    def test_daily_granularity_is_accepted(
        self, authenticated_client
    ):
        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/",
            {"granularity": "daily"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["granularity"] == "daily"

    def test_weekly_granularity_is_accepted(
        self, authenticated_client
    ):
        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/",
            {"granularity": "weekly"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["granularity"] == "weekly"

    def test_monthly_granularity_is_accepted(
        self, authenticated_client
    ):
        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/",
            {"granularity": "monthly"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["granularity"] == "monthly"

    def test_invalid_granularity_returns_400(
        self, authenticated_client
    ):
        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/",
            {"granularity": "yearly"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_start_date_returns_400(
        self, authenticated_client
    ):
        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/",
            {"start_date": "not-a-date"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_start_date_after_end_date_returns_400(
        self, authenticated_client
    ):
        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/",
            {
                "start_date": "2026-11-20",
                "end_date": "2026-11-01",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_analytics_requires_authentication(self, api_client):
        response = api_client.get(
            "/api/v1/dashboard/analytics/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAnalyticsCSVExport:

    def test_csv_export_returns_csv_file(
        self, authenticated_client, user, company
    ):
        create_analytics_application(
            user,
            company,
            "CSV Export Developer",
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/export/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"].startswith("text/csv")
        assert "attachment;" in response["Content-Disposition"]

        content = response.content.decode("utf-8")

        assert "Company" in content
        assert "Job Title" in content
        assert "CSV Export Developer" in content

    def test_csv_export_only_contains_current_users_data(
        self,
        authenticated_client,
        user,
        another_user,
        company,
    ):
        create_analytics_application(
            user,
            company,
            "My Private Application",
        )

        create_analytics_application(
            another_user,
            company,
            "Other Private Application",
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/export/"
        )

        content = response.content.decode("utf-8")

        assert "My Private Application" in content
        assert "Other Private Application" not in content

    def test_csv_export_respects_date_range(
        self, authenticated_client, user, company
    ):
        today = timezone.localdate()

        create_analytics_application(
            user,
            company,
            "Recent Application",
            applied_date=today,
        )

        create_analytics_application(
            user,
            company,
            "Old Application",
            applied_date=today - timedelta(days=90),
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/analytics/export/",
            {
                "start_date": (today - timedelta(days=10)).isoformat(),
                "end_date": today.isoformat(),
            },
        )

        content = response.content.decode("utf-8")

        assert "Recent Application" in content
        assert "Old Application" not in content

    def test_csv_export_requires_authentication(self, api_client):
        response = api_client.get(
            "/api/v1/dashboard/analytics/export/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED