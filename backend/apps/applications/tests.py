import pytest

from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from apps.companies.models import Company
from apps.applications.models import (
    ApplicationNote,
    ApplicationStatusHistory,
    JobApplication,
)

from apps.applications.choices import ApplicationStatus

User = get_user_model()


@pytest.mark.django_db
class TestJobApplicationModel:

    def setup_method(self):

        self.user = User.objects.create_user(
            email="rahul@example.com",
            password="SecurePass123!",
            first_name="Rahul",
        )

        self.company = Company.objects.create(
            name="Google",
        )

    def test_create_application(self):

        application = JobApplication.objects.create(
            user=self.user,
            company=self.company,
            job_title="Python Developer",
        )

        assert application.id is not None
        assert application.status == "applied"
        assert application.user == self.user

    def test_default_applied_date(self):

        application = JobApplication.objects.create(
            user=self.user,
            company=self.company,
            job_title="Backend Developer",
        )

        assert application.applied_date == timezone.localdate()

    def test_salary_range_constraint(self):

        with pytest.raises(IntegrityError):

            with transaction.atomic():

                JobApplication.objects.create(
                    user=self.user,
                    company=self.company,
                    job_title="Python Developer",
                    salary_min=Decimal("1000000"),
                    salary_max=Decimal("500000"),
                )

    def test_negative_salary_constraint(self):

        with pytest.raises(IntegrityError):

            with transaction.atomic():

                JobApplication.objects.create(
                    user=self.user,
                    company=self.company,
                    job_title="Python Developer",
                    salary_min=Decimal("-1000"),
                )

    def test_deadline_constraint(self):

        with pytest.raises(IntegrityError):

            with transaction.atomic():

                JobApplication.objects.create(
                    user=self.user,
                    company=self.company,
                    job_title="Python Developer",
                    applied_date=date.today(),
                    deadline=date.today() - timedelta(days=1),
                )

    def test_application_string_representation(self):

        application = JobApplication.objects.create(
            user=self.user,
            company=self.company,
            job_title="Backend Developer",
        )

        assert str(application) == "Backend Developer at Google"

    def test_user_can_have_multiple_applications(self):

        for title in [
            "Python Developer",
            "Backend Engineer",
            "Software Engineer",
        ]:
            JobApplication.objects.create(
                user=self.user,
                company=self.company,
                job_title=title,
            )

        assert self.user.applications.count() == 3

    def test_company_protected_from_deletion(self):

        JobApplication.objects.create(
            user=self.user,
            company=self.company,
            job_title="Python Developer",
        )

        from django.db.models import ProtectedError

        with pytest.raises(ProtectedError):
            self.company.delete()


@pytest.mark.django_db
class TestApplicationHistory:

    def test_create_status_history(self):

        user = User.objects.create_user(
            email="history@example.com",
            password="SecurePass123!",
            first_name="History",
        )

        company = Company.objects.create(
            name="Infosys",
        )

        application = JobApplication.objects.create(
            user=user,
            company=company,
            job_title="Software Engineer",
        )

        history = ApplicationStatusHistory.objects.create(
            application=application,
            old_status=None,
            new_status=ApplicationStatus.APPLIED,
            changed_by=user,
        )

        assert history.application == application
        assert history.new_status == "applied"

    def test_same_old_and_new_status_rejected(self):

        user = User.objects.create_user(
            email="status@example.com",
            password="SecurePass123!",
            first_name="Status",
        )

        company = Company.objects.create(
            name="TCS",
        )

        application = JobApplication.objects.create(
            user=user,
            company=company,
            job_title="Developer",
        )

        with pytest.raises(IntegrityError):

            with transaction.atomic():

                ApplicationStatusHistory.objects.create(
                    application=application,
                    old_status="applied",
                    new_status="applied",
                )


@pytest.mark.django_db
class TestApplicationNotes:

    def test_create_application_note(self):

        user = User.objects.create_user(
            email="notes@example.com",
            password="SecurePass123!",
            first_name="Notes",
        )

        company = Company.objects.create(
            name="Wipro",
        )

        application = JobApplication.objects.create(
            user=user,
            company=company,
            job_title="Python Developer",
        )

        note = ApplicationNote.objects.create(
            application=application,
            created_by=user,
            title="Interview preparation",
            content="Revise Python and SQL.",
        )

        assert note.application == application
        assert note.created_by == user
        assert note.content == "Revise Python and SQL."