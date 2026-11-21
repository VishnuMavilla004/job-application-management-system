import pytest

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.companies.models import Company
from apps.applications.models import JobApplication
from apps.interviews.models import Interview

User = get_user_model()


@pytest.mark.django_db
class TestInterviewModel:

    def test_create_interview(self):

        user = User.objects.create_user(
            email="interview@example.com",
            password="SecurePass123!",
            first_name="Interview",
        )

        company = Company.objects.create(
            name="Microsoft",
        )

        application = JobApplication.objects.create(
            user=user,
            company=company,
            job_title="Software Engineer",
        )

        interview = Interview.objects.create(
            application=application,
            interview_type="technical",
            scheduled_at=timezone.now() + timedelta(days=2),
            interviewer_name="Technical Lead",
        )

        assert interview.id is not None
        assert interview.outcome == "pending"
        assert interview.application == application

    def test_multiple_interviews(self):

        user = User.objects.create_user(
            email="rounds@example.com",
            password="SecurePass123!",
            first_name="Rounds",
        )

        company = Company.objects.create(
            name="Amazon",
        )

        application = JobApplication.objects.create(
            user=user,
            company=company,
            job_title="Backend Developer",
        )

        for interview_type in ["technical", "hr"]:

            Interview.objects.create(
                application=application,
                interview_type=interview_type,
                scheduled_at=timezone.now() + timedelta(days=1),
            )

        assert application.interviews.count() == 2