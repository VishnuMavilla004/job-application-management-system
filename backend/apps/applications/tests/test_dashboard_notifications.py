from datetime import date

import pytest

from django.utils import timezone
from rest_framework import status

from apps.applications.models import (
    ApplicationNotification,
    JobApplication,
)


pytestmark = pytest.mark.django_db


def create_dashboard_application(
    user,
    company,
    title,
    application_status="applied",
    employment_type="full_time",
    applied_date=None,
):
    return JobApplication.objects.create(
        user=user,
        company=company,
        job_title=title,
        location="Bengaluru",
        employment_type=employment_type,
        work_mode="hybrid",
        salary_min=500000,
        salary_max=900000,
        status=application_status,
        applied_date=applied_date or timezone.localdate(),
    )


class TestDashboardSummary:

    def test_dashboard_summary_returns_correct_metrics(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_dashboard_application(
            user,
            company,
            "Applied Developer",
            "applied",
        )

        create_dashboard_application(
            user,
            company,
            "Assessment Developer",
            "assessment",
        )

        create_dashboard_application(
            user,
            company,
            "Interview Developer",
            "interview",
        )

        create_dashboard_application(
            user,
            company,
            "Offer Developer",
            "offer",
        )

        create_dashboard_application(
            user,
            company,
            "Rejected Developer",
            "rejected",
        )

        create_dashboard_application(
            user,
            company,
            "Withdrawn Developer",
            "withdrawn",
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/summary/"
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.data["data"]

        assert data["total_applications"] == 6
        assert data["active_applications"] == 3
        assert data["interviews"] == 2
        assert data["offers"] == 1
        assert data["rejections"] == 1
        assert data["withdrawals"] == 1

        assert data["interview_conversion_rate"] == 33.33
        assert data["offer_conversion_rate"] == 16.67

    def test_dashboard_returns_zero_values_without_applications(
        self,
        authenticated_client,
    ):
        response = authenticated_client.get(
            "/api/v1/dashboard/summary/"
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.data["data"]

        assert data["total_applications"] == 0
        assert data["offers"] == 0
        assert data["offer_conversion_rate"] == 0.0

    def test_dashboard_summary_includes_unread_notifications(
        self,
        authenticated_client,
        user,
    ):
        ApplicationNotification.objects.create(
            user=user,
            notification_type="application_created",
            title="Test notification",
            message="Test message",
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/summary/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["unread_notifications"] == 1

    def test_dashboard_summary_requires_authentication(
        self,
        api_client,
    ):
        response = api_client.get(
            "/api/v1/dashboard/summary/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDashboardDistribution:

    def test_status_distribution(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_dashboard_application(
            user,
            company,
            "Applied One",
            "applied",
        )

        create_dashboard_application(
            user,
            company,
            "Applied Two",
            "applied",
        )

        create_dashboard_application(
            user,
            company,
            "Interview One",
            "interview",
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/distribution/"
        )

        assert response.status_code == status.HTTP_200_OK

        distribution = response.data["data"]["status_distribution"]

        counts = {
            item["status"]: item["count"]
            for item in distribution
        }

        assert counts["applied"] == 2
        assert counts["interview"] == 1
        assert counts["offer"] == 0

    def test_employment_type_distribution(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_dashboard_application(
            user,
            company,
            "Full Time One",
            employment_type="full_time",
        )

        create_dashboard_application(
            user,
            company,
            "Full Time Two",
            employment_type="full_time",
        )

        create_dashboard_application(
            user,
            company,
            "Internship One",
            employment_type="internship",
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/distribution/"
        )

        assert response.status_code == status.HTTP_200_OK

        distribution = response.data["data"][
            "employment_type_distribution"
        ]

        counts = {
            item["employment_type"]: item["count"]
            for item in distribution
        }

        assert counts["full_time"] == 2
        assert counts["internship"] == 1


class TestDashboardTrends:

    def test_trends_return_six_months(
        self,
        authenticated_client,
        user,
        company,
    ):
        response = authenticated_client.get(
            "/api/v1/dashboard/trends/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 6

    def test_trends_include_current_month_application(
        self,
        authenticated_client,
        user,
        company,
    ):
        create_dashboard_application(
            user,
            company,
            "Current Month Application",
            applied_date=timezone.localdate(),
        )

        response = authenticated_client.get(
            "/api/v1/dashboard/trends/"
        )

        assert response.status_code == status.HTTP_200_OK

        current_month = timezone.localdate().strftime("%Y-%m")

        matching_month = next(
            item
            for item in response.data["data"]
            if item["month"] == current_month
        )

        assert matching_month["count"] == 1


class TestNotificationCreation:

    def test_application_creation_creates_notification(
        self,
        authenticated_client,
        company,
        user,
    ):
        response = authenticated_client.post(
            "/api/v1/applications/",
            {
                "company_id": company.id,
                "job_title": "Notification Test Developer",
                "employment_type": "full_time",
                "work_mode": "remote",
                "status": "applied",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        notification = ApplicationNotification.objects.get(
            user=user,
            notification_type="application_created",
        )

        assert notification.is_read is False
        assert "Notification Test Developer" in notification.message

    def test_status_update_creates_notification(
        self,
        authenticated_client,
        application,
        user,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "assessment",
                "remarks": "Assessment received.",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        notification = ApplicationNotification.objects.get(
            user=user,
            notification_type="status_changed",
        )

        assert "assessment" in notification.message


class TestNotificationAPI:

    def test_user_can_list_own_notifications(
        self,
        authenticated_client,
        user,
    ):
        ApplicationNotification.objects.create(
            user=user,
            notification_type="application_created",
            title="Application created",
            message="Test notification",
        )

        response = authenticated_client.get(
            "/api/v1/notifications/"
        )

        assert response.status_code == status.HTTP_200_OK

        assert response.data["count"] == 1
        assert response.data["unread_count"] == 1
        assert len(response.data["results"]) == 1

    def test_user_can_mark_notification_as_read(
        self,
        authenticated_client,
        user,
    ):
        notification = ApplicationNotification.objects.create(
            user=user,
            notification_type="application_created",
            title="Application created",
            message="Test notification",
        )

        response = authenticated_client.patch(
            f"/api/v1/notifications/{notification.id}/read/"
        )

        assert response.status_code == status.HTTP_200_OK

        notification.refresh_from_db()

        assert notification.is_read is True

    def test_user_can_mark_all_notifications_as_read(
        self,
        authenticated_client,
        user,
    ):
        for number in range(3):
            ApplicationNotification.objects.create(
                user=user,
                notification_type="application_created",
                title=f"Notification {number}",
                message="Test notification",
            )

        response = authenticated_client.patch(
            "/api/v1/notifications/read-all/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["updated_count"] == 3

        assert ApplicationNotification.objects.filter(
            user=user,
            is_read=False,
        ).count() == 0

    def test_user_cannot_read_another_users_notification(
        self,
        authenticated_client,
        another_user,
    ):
        notification = ApplicationNotification.objects.create(
            user=another_user,
            notification_type="application_created",
            title="Private notification",
            message="Private message",
        )

        response = authenticated_client.patch(
            f"/api/v1/notifications/{notification.id}/read/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_notification_list_does_not_expose_other_users_notifications(
        self,
        authenticated_client,
        another_user,
        user,
    ):
        ApplicationNotification.objects.create(
            user=another_user,
            notification_type="application_created",
            title="Other user's notification",
            message="Private message",
        )

        ApplicationNotification.objects.create(
            user=user,
            notification_type="application_created",
            title="My notification",
            message="My message",
        )

        response = authenticated_client.get(
            "/api/v1/notifications/"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_notification_endpoints_require_authentication(
        self,
        api_client,
    ):
        response = api_client.get(
            "/api/v1/notifications/"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED