from django.contrib import admin

from .models import (
    ApplicationNote,
    ApplicationStatusHistory,
    JobApplication,
)

from apps.applications.models import ApplicationNotification


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "job_title",
        "company",
        "user",
        "status",
        "applied_date",
    )

    list_filter = (
        "status",
        "employment_type",
        "work_mode",
    )

    search_fields = (
        "job_title",
        "company__name",
        "user__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "application",
        "old_status",
        "new_status",
        "changed_by",
        "changed_at",
    )

    readonly_fields = (
        "changed_at",
    )


@admin.register(ApplicationNote)
class ApplicationNoteAdmin(admin.ModelAdmin):

    list_display = (
        "application",
        "title",
        "created_by",
        "created_at",
    )

    search_fields = (
        "title",
        "content",
        "application__job_title",
    )

@admin.register(ApplicationNotification)
class ApplicationNotificationAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "user",
        "notification_type",
        "title",
        "is_read",
        "created_at",
    ]

    list_filter = [
        "notification_type",
        "is_read",
        "created_at",
    ]

    search_fields = [
        "user__email",
        "title",
        "message",
    ]

    readonly_fields = [
        "created_at",
    ]