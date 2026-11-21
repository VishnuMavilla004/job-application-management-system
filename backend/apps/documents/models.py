from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.validators import FileExtensionValidator

from .validators import validate_file_size


def resume_upload_path(instance, filename):
    return f"users/{instance.user_id}/resumes/{filename}"


class ResumeDocument(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
    )

    title = models.CharField(max_length=200)

    file = models.FileField(
        upload_to=resume_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx"]
            ),
            validate_file_size,
        ],
    )

    is_default = models.BooleanField(default=False)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "resume_documents"
        ordering = ["-uploaded_at"]

        indexes = [
            models.Index(
                fields=["user", "is_default"],
                name="resume_user_default_idx",
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_default=True),
                name="one_default_resume_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"