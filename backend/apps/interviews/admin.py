from django.contrib import admin
from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):

    list_display = (
        "application",
        "interview_type",
        "scheduled_at",
        "outcome",
    )

    list_filter = (
        "interview_type",
        "outcome",
    )

    search_fields = (
        "application__job_title",
        "interviewer_name",
    )