from django.conf import settings
from django.db import models

from apps.applications.choices import (
    InterviewOutcome,
    InterviewType,
)
from apps.applications.models import JobApplication


class Interview(models.Model):

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="interviews",
    )

    interview_type = models.CharField(
        max_length=20,
        choices=InterviewType.choices,
    )

    scheduled_at = models.DateTimeField()

    duration_minutes = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    meeting_link = models.URLField(
        blank=True,
    )

    location = models.CharField(
        max_length=200,
        blank=True,
    )

    interviewer_name = models.CharField(
        max_length=150,
        blank=True,
    )

    outcome = models.CharField(
        max_length=20,
        choices=InterviewOutcome.choices,
        default=InterviewOutcome.PENDING,
    )

    feedback = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "interviews"

        ordering = ["scheduled_at"]

        indexes = [
            models.Index(
                fields=["application", "scheduled_at"],
                name="interview_app_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.interview_type} interview - "
            f"{self.application.job_title}"
        )