from rest_framework import serializers

from apps.applications.models import (
    JobApplication,
    ApplicationStatusHistory,
)
from apps.companies.models import Company
from apps.companies.serializers import CompanySerializer

from apps.applications.services import validate_status_transition


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.EmailField(
        source="changed_by.email",
        read_only=True,
        default=None,
    )

    class Meta:
        model = ApplicationStatusHistory
        fields = [
            "id",
            "old_status",
            "new_status",
            "changed_by",
            "changed_by_email",
            "changed_at",
            "remarks",
        ]
        read_only_fields = fields


class JobApplicationSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source="company",
        write_only=True,
    )

    status_history = ApplicationStatusHistorySerializer(
    many=True,
    read_only=True,
    )

    class Meta:
        model = JobApplication
        fields = [
        "id",
        "company",
        "company_id",
        "job_title",
        "job_description",
        "location",
        "employment_type",
        "work_mode",
        "salary_min",
        "salary_max",
        "job_url",
        "status",
        "applied_date",
        "deadline",
        "contact_person",
        "contact_email",
        "status_history",
        "created_at",
        "updated_at",
        ]

        read_only_fields = [
            "id",
            "status_history",
            "created_at",
            "updated_at",
        ]

    def validate_job_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Job title cannot be empty.")

        return value

    def validate(self, attrs):
        from apps.applications.services import validate_status_transition

        salary_min = attrs.get(
            "salary_min",
            getattr(self.instance, "salary_min", None),
        )

        salary_max = attrs.get(
            "salary_max",
            getattr(self.instance, "salary_max", None),
        )

        applied_date = attrs.get(
            "applied_date",
            getattr(self.instance, "applied_date", None),
        )

        deadline = attrs.get(
            "deadline",
            getattr(self.instance, "deadline", None),
        )

        new_status = attrs.get("status")

        # Salary validation
        if salary_min is not None and salary_min < 0:
            raise serializers.ValidationError({
                "salary_min": "Minimum salary cannot be negative."
            })

        if salary_max is not None and salary_max < 0:
            raise serializers.ValidationError({
                "salary_max": "Maximum salary cannot be negative."
            })

        if (
            salary_min is not None
            and salary_max is not None
            and salary_max < salary_min
        ):
            raise serializers.ValidationError({
                "salary_max": (
                    "Maximum salary cannot be less than minimum salary."
                )
            })

        # Date validation
        if (
            applied_date is not None
            and deadline is not None
            and deadline < applied_date
        ):
            raise serializers.ValidationError({
                "deadline": (
                    "Deadline cannot be earlier than the applied date."
                )
            })

        # Prevent future application dates
        from django.utils import timezone

        if (
            applied_date is not None
            and applied_date > timezone.localdate()
        ):
            raise serializers.ValidationError({
                "applied_date": (
                    "Application date cannot be in the future."
                )
            })

        # Status transition validation on normal PATCH/PUT requests
        if self.instance is not None and new_status is not None:
            validate_status_transition(
                current_status=self.instance.status,
                new_status=new_status,
            )

        return attrs

class ApplicationStatusUpdateSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=[
            ("applied", "Applied"),
            ("assessment", "Assessment"),
            ("interview", "Interview"),
            ("offer", "Offer"),
            ("rejected", "Rejected"),
            ("withdrawn", "Withdrawn"),
        ]
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        default="",
    )

    def validate_status(self, value):
        application = self.context["application"]

        validate_status_transition(
            current_status=application.status,
            new_status=value,
        )

        return value