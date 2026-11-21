import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.documents.models import ResumeDocument
from apps.documents.validators import validate_file_size

User = get_user_model()


@pytest.mark.django_db
class TestResumeDocument:

    def setup_method(self):

        self.user = User.objects.create_user(
            email="resume@example.com",
            password="SecurePass123!",
            first_name="Resume",
        )

    def test_create_resume(self):

        file = SimpleUploadedFile(
            "resume.pdf",
            b"Sample PDF content",
            content_type="application/pdf",
        )

        resume = ResumeDocument.objects.create(
            user=self.user,
            title="Python Developer Resume",
            file=file,
        )

        assert resume.id is not None
        assert resume.user == self.user
        assert resume.is_default is False

    def test_default_resume_constraint(self):

        ResumeDocument.objects.create(
            user=self.user,
            title="Resume 1",
            file="users/1/resumes/resume1.pdf",
            is_default=True,
        )

        from django.db import IntegrityError, transaction

        with pytest.raises(IntegrityError):

            with transaction.atomic():

                ResumeDocument.objects.create(
                    user=self.user,
                    title="Resume 2",
                    file="users/1/resumes/resume2.pdf",
                    is_default=True,
                )

    def test_file_size_validation(self):

        file = SimpleUploadedFile(
            "large.pdf",
            b"x" * (6 * 1024 * 1024),
        )

        with pytest.raises(ValidationError):
            validate_file_size(file)

    def test_resume_string_representation(self):

        resume = ResumeDocument(
            user=self.user,
            title="Backend Resume",
            file="resume.pdf",
        )

        assert str(resume) == (
            "Backend Resume - resume@example.com"
        )