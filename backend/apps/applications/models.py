from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.companies.models import Company
from .choices import (
    ApplicationStatus,
    EmploymentType,
    WorkMode,
)



class JobApplication(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="applications",
    )

    job_title = models.CharField(
        max_length=200,
    )

    job_description = models.TextField(
        blank=True,
    )

    location = models.CharField(
        max_length=200,
        blank=True,
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )

    work_mode = models.CharField(
        max_length=20,
        choices=WorkMode.choices,
        default=WorkMode.ONSITE,
    )

    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    job_url = models.URLField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.APPLIED,
    )

    applied_date = models.DateField(
        default=timezone.localdate,
    )

    deadline = models.DateField(
        null=True,
        blank=True,
    )

    contact_person = models.CharField(
        max_length=150,
        blank=True,
    )

    contact_email = models.EmailField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "job_applications"

        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "status"],
                name="app_user_status_idx",
            ),
            models.Index(
                fields=["user", "applied_date"],
                name="app_user_date_idx",
            ),
            models.Index(
                fields=["company"],
                name="app_company_idx",
            ),
        ]

        constraints = [
    models.CheckConstraint(
        condition=(
            Q(salary_max__isnull=True)
            | Q(salary_min__isnull=True)
            | Q(salary_max__gte=F("salary_min"))
        ),
        name="valid_salary_range",
    ),

    models.CheckConstraint(
        condition=(
            Q(deadline__isnull=True)
            | Q(deadline__gte=F("applied_date"))
        ),
        name="valid_application_deadline",
    ),

    models.CheckConstraint(
        condition=(
            Q(salary_min__isnull=True)
            | Q(salary_min__gte=0)
        ),
        name="nonnegative_salary_min",
    ),

    models.CheckConstraint(
        condition=(
            Q(salary_max__isnull=True)
            | Q(salary_max__gte=0)
        ),
        name="nonnegative_salary_max",
    ),
]

    def __str__(self):
        return f"{self.job_title} at {self.company.name}"

class ApplicationStatusHistory(models.Model):

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="status_history",
    )

    old_status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        null=True,
        blank=True,
    )

    new_status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="status_changes",
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "application_status_history"

        ordering = ["-changed_at"]

        indexes = [
            models.Index(
                fields=["application", "-changed_at"],
                name="status_app_date_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(old_status__isnull=True)
                    | ~Q(old_status=F("new_status"))
                ),
                name="different_application_status",
            ),
        ]

    def __str__(self):
        return (
            f"{self.application_id}: "
            f"{self.old_status} -> {self.new_status}"
        )

class ApplicationNote(models.Model):

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="notes",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_notes",
    )

    title = models.CharField(
        max_length=200,
        blank=True,
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "application_notes"

        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["application", "-created_at"],
                name="note_app_date_idx",
            ),
        ]

        models.CheckConstraint(
            condition=(
                Q(salary_min__isnull=True)
                | Q(salary_min__gte=0)
            ),
            name="nonnegative_salary_min",
        ),

        models.CheckConstraint(
            condition=(
                Q(salary_max__isnull=True)
                | Q(salary_max__gte=0)
            ),
            name="nonnegative_salary_max",
        ),

    def __str__(self):
        return (
            f"Note for {self.application.job_title}"
        )

class ApplicationNotification(models.Model):

    class NotificationType(models.TextChoices):
        APPLICATION_CREATED = (
            "application_created",
            "Application Created",
        )
        STATUS_CHANGED = (
            "status_changed",
            "Status Changed",
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="application_notifications",
    )

    application = models.ForeignKey(
        "applications.JobApplication",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "is_read", "-created_at"],
                name="appnotif_user_read_idx",
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"