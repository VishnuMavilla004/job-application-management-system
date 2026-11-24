from rest_framework import serializers

from apps.applications.models import ApplicationNotification


class ApplicationNotificationSerializer(serializers.ModelSerializer):

    application_job_title = serializers.CharField(
        source="application.job_title",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ApplicationNotification

        fields = [
            "id",
            "application",
            "application_job_title",
            "notification_type",
            "title",
            "message",
            "is_read",
            "created_at",
        ]

        read_only_fields = fields