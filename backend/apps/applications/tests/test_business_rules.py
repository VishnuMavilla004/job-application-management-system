from datetime import timedelta

import pytest

from django.utils import timezone
from rest_framework import status

from apps.applications.models import (
    ApplicationStatusHistory,
    JobApplication,
)
from apps.applications.services import (
    ALLOWED_STATUS_TRANSITIONS,
    validate_status_transition,
)


pytestmark = pytest.mark.django_db



from datetime import timedelta

import pytest

from django.utils import timezone
from rest_framework import status

from apps.applications.models import (
    ApplicationStatusHistory,
    JobApplication,
)
from apps.applications.services import (
    ALLOWED_STATUS_TRANSITIONS,
    validate_status_transition,
)


pytestmark = pytest.mark.django_db


class TestStatusTransitionRules:

    @pytest.mark.parametrize(
        "current,new",
        [
            ("applied", "assessment"),
            ("applied", "interview"),
            ("applied", "rejected"),
            ("applied", "withdrawn"),
            ("assessment", "interview"),
            ("assessment", "rejected"),
            ("assessment", "withdrawn"),
            ("interview", "offer"),
            ("interview", "rejected"),
            ("interview", "withdrawn"),
            ("offer", "withdrawn"),
        ],
    )
    def test_valid_transitions(self, current, new):
        assert new in ALLOWED_STATUS_TRANSITIONS[current]
        validate_status_transition(current, new)

    @pytest.mark.parametrize(
        "current,new",
        [
            ("applied", "offer"),
            ("assessment", "applied"),
            ("interview", "applied"),
            ("offer", "interview"),
            ("rejected", "interview"),
            ("withdrawn", "applied"),
        ],
    )
    def test_invalid_transitions_are_rejected(self, current, new):
        from rest_framework.exceptions import ValidationError

        with pytest.raises(ValidationError):
            validate_status_transition(current, new)

    @pytest.mark.parametrize(
        "terminal_status",
        ["rejected", "withdrawn"],
    )
    def test_terminal_statuses_have_no_outgoing_transitions(
        self,
        terminal_status,
    ):
        assert ALLOWED_STATUS_TRANSITIONS[terminal_status] == set()

    def test_same_status_transition_is_rejected(self):
        from rest_framework.exceptions import ValidationError

        with pytest.raises(ValidationError):
            validate_status_transition("applied", "applied")


class TestDedicatedStatusAPI:

    def test_user_can_update_application_status(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "assessment",
                "remarks": "Online assessment received.",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["old_status"] == "applied"
        assert response.data["data"]["new_status"] == "assessment"

        application.refresh_from_db()

        assert application.status == "assessment"

    def test_status_change_creates_history(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "interview",
                "remarks": "Technical interview scheduled.",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        history = ApplicationStatusHistory.objects.get(
            application=application,
            old_status="applied",
            new_status="interview",
        )

        assert history.remarks == "Technical interview scheduled."

    def test_invalid_transition_is_rejected(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "offer",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        application.refresh_from_db()

        assert application.status == "applied"

    def test_same_status_update_is_rejected(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "applied",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejected_application_cannot_be_reopened(
        self,
        authenticated_client,
        application,
    ):
        application.status = "rejected"
        application.save(update_fields=["status"])

        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "interview",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_withdrawn_application_cannot_be_reopened(
        self,
        authenticated_client,
        application,
    ):
        application.status = "withdrawn"
        application.save(update_fields=["status"])

        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "applied",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_status_remarks_are_optional(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "assessment",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

    def test_status_remarks_cannot_exceed_500_characters(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "assessment",
                "remarks": "A" * 501,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_user_cannot_update_status(
        self,
        api_client,
        application,
    ):
        response = api_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "assessment",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_another_user_cannot_update_status(
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
            f"/api/v1/applications/{other_application.id}/status/",
            {
                "status": "assessment",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        other_application.refresh_from_db()

        assert other_application.status == "applied"

    def test_invalid_status_choice_is_rejected(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/status/",
            {
                "status": "hired",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestNormalUpdateBusinessRules:

    def test_normal_patch_obeys_transition_rules(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "status": "offer",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        application.refresh_from_db()

        assert application.status == "applied"

    def test_normal_patch_allows_valid_status_transition(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "status": "assessment",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        application.refresh_from_db()

        assert application.status == "assessment"

        assert ApplicationStatusHistory.objects.filter(
            application=application,
            old_status="applied",
            new_status="assessment",
        ).exists()

    def test_normal_patch_records_supplied_remarks(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "status": "assessment",
                "remarks": "Assessment invitation received.",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        history = ApplicationStatusHistory.objects.get(
            application=application,
            old_status="applied",
            new_status="assessment",
        )

        assert history.remarks == "Assessment invitation received."

    def test_user_cannot_change_application_owner(
        self,
        authenticated_client,
        application,
        another_user,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "user": another_user.id,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        application.refresh_from_db()

        assert application.user != another_user

    def test_patch_job_title_without_changing_status(
        self,
        authenticated_client,
        application,
    ):
        original_status = application.status

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
        assert application.status == original_status

    def test_patch_location_and_salary_without_changing_status(
        self,
        authenticated_client,
        application,
    ):
        original_status = application.status

        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "location": "Bengaluru, India",
                "salary_min": "600000",
                "salary_max": "900000",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        application.refresh_from_db()

        assert application.location == "Bengaluru, India"
        assert application.salary_min == 600000
        assert application.salary_max == 900000
        assert application.status == original_status


class TestAdvancedValidation:

    def test_negative_minimum_salary_is_rejected(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "salary_min": -1000,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_negative_maximum_salary_is_rejected(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "salary_max": -1000,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_maximum_salary_cannot_be_below_minimum_salary(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "salary_min": 1000000,
                "salary_max": 500000,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_future_applied_date_is_rejected(
        self,
        authenticated_client,
        application,
    ):
        future_date = (
            timezone.localdate() + timedelta(days=5)
        )

        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "applied_date": future_date.isoformat(),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_deadline_before_applied_date_is_rejected(
        self,
        authenticated_client,
        application,
    ):
        response = authenticated_client.patch(
            f"/api/v1/applications/{application.id}/",
            {
                "applied_date": "2026-06-15",
                "deadline": "2026-06-10",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
