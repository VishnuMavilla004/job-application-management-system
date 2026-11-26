
from rest_framework import serializers

from apps.documents.models import ResumeDocument


class ResumeDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ResumeDocument
        fields = (
            "id",
            "title",
            "file",
            "file_url",
            "is_default",
            "uploaded_at",
        )
        read_only_fields = (
            "id",
            "file_url",
            "uploaded_at",
        )

    def get_file_url(self, obj):
        request = self.context.get("request")

        if not obj.file:
            return None

        url = obj.file.url

        return request.build_absolute_uri(url) if request else url

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Resume title cannot be empty."
            )

        return value

    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError(
                "A resume file is required."
            )

        return value
