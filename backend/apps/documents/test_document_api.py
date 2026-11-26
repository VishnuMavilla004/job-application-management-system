
import pytest

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework.test import APIClient

from apps.documents.models import ResumeDocument

User = get_user_model()


def make_pdf(name="resume.pdf", content=b"%PDF-1.4\nSample resume\n%%EOF"):
    return SimpleUploadedFile(
        name,
        content,
        content_type="application/pdf",
    )


@pytest.mark.django_db
class TestResumeAPI:

    def setup_method(self):
        self.user = User.objects.create_user(
            email="resume-api@example.com",
            password="SecurePass123!",
            first_name="Resume",
        )

        self.other_user = User.objects.create_user(
            email="other-resume@example.com",
            password="SecurePass123!",
            first_name="Other",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.list_url = reverse("resume-list-create")

    def upload_resume(self, title="Python Developer", is_default=False):
        return self.client.post(
            self.list_url,
            {
                "title": title,
                "file": make_pdf(),
                "is_default": is_default,
            },
            format="multipart",
        )

    def test_upload_resume(self):
        response = self.upload_resume()

        assert response.status_code == 201
        assert response.data["success"] is True
        assert ResumeDocument.objects.filter(
            user=self.user
        ).count() == 1

    def test_list_only_current_users_resumes(self):
        ResumeDocument.objects.create(
            user=self.user,
            title="My Resume",
            file="resumes/my-resume.pdf",
        )

        ResumeDocument.objects.create(
            user=self.other_user,
            title="Other Resume",
            file="resumes/other-resume.pdf",
        )

        response = self.client.get(self.list_url)

        assert response.status_code == 200
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["title"] == "My Resume"

    def test_retrieve_resume(self):
        resume = ResumeDocument.objects.create(
            user=self.user,
            title="Backend Resume",
            file="resumes/backend.pdf",
        )

        response = self.client.get(
            reverse("resume-detail", args=[resume.pk])
        )

        assert response.status_code == 200
        assert response.data["data"]["title"] == "Backend Resume"

    def test_user_cannot_retrieve_another_users_resume(self):
        resume = ResumeDocument.objects.create(
            user=self.other_user,
            title="Private Resume",
            file="resumes/private.pdf",
        )

        response = self.client.get(
            reverse("resume-detail", args=[resume.pk])
        )

        assert response.status_code == 404

    def test_update_resume_title(self):
        resume = ResumeDocument.objects.create(
            user=self.user,
            title="Old Title",
            file="resumes/update.pdf",
        )

        response = self.client.patch(
            reverse("resume-detail", args=[resume.pk]),
            {"title": "Updated Title"},
            format="json",
        )

        assert response.status_code == 200

        resume.refresh_from_db()
        assert resume.title == "Updated Title"

    def test_only_one_default_resume(self):
        first = self.upload_resume(
            title="First Resume",
            is_default=True,
        )

        second = self.upload_resume(
            title="Second Resume",
            is_default=True,
        )

        assert first.status_code == 201
        assert second.status_code == 201

        defaults = ResumeDocument.objects.filter(
            user=self.user,
            is_default=True,
        )

        assert defaults.count() == 1
        assert defaults.first().title == "Second Resume"

    def test_set_default_resume(self):
        first = self.upload_resume(
            title="First Resume",
            is_default=True,
        )

        second = self.upload_resume(
            title="Second Resume",
        )

        first_id = first.data["data"]["id"]
        second_id = second.data["data"]["id"]

        response = self.client.post(
            reverse("resume-set-default", args=[second_id])
        )

        assert response.status_code == 200

        assert ResumeDocument.objects.get(
            pk=second_id
        ).is_default is True

        assert ResumeDocument.objects.get(
            pk=first_id
        ).is_default is False

    def test_user_cannot_set_another_users_resume_as_default(self):
        resume = ResumeDocument.objects.create(
            user=self.other_user,
            title="Private Resume",
            file="resumes/private.pdf",
        )

        response = self.client.post(
            reverse("resume-set-default", args=[resume.pk])
        )

        assert response.status_code == 404

    def test_delete_resume(self):
        resume = ResumeDocument.objects.create(
            user=self.user,
            title="Delete Me",
            file="resumes/delete-me.pdf",
        )

        response = self.client.delete(
            reverse("resume-detail", args=[resume.pk])
        )

        assert response.status_code == 200
        assert not ResumeDocument.objects.filter(
            pk=resume.pk
        ).exists()

    def test_delete_default_promotes_newest_remaining_resume(self):
        first = ResumeDocument.objects.create(
            user=self.user,
            title="First",
            file="resumes/first.pdf",
            is_default=True,
        )

        second = ResumeDocument.objects.create(
            user=self.user,
            title="Second",
            file="resumes/second.pdf",
        )

        response = self.client.delete(
            reverse("resume-detail", args=[first.pk])
        )

        assert response.status_code == 200

        second.refresh_from_db()
        assert second.is_default is True

    def test_download_resume(self):
        response = self.upload_resume()

        resume_id = response.data["data"]["id"]

        download_response = self.client.get(
            reverse("resume-download", args=[resume_id])
        )

        assert download_response.status_code == 200
        assert download_response["Content-Disposition"].startswith(
            "attachment;"
        )

    def test_invalid_extension_is_rejected(self):
        invalid_file = SimpleUploadedFile(
            "resume.exe",
            b"not a valid resume",
            content_type="application/octet-stream",
        )

        response = self.client.post(
            self.list_url,
            {
                "title": "Invalid Resume",
                "file": invalid_file,
            },
            format="multipart",
        )

        assert response.status_code == 400
        assert ResumeDocument.objects.filter(
            user=self.user
        ).count() == 0

    def test_oversized_resume_is_rejected(self):
        large_file = SimpleUploadedFile(
            "large.pdf",
            b"%PDF-1.4\n" + b"x" * (6 * 1024 * 1024),
            content_type="application/pdf",
        )

        response = self.client.post(
            self.list_url,
            {
                "title": "Large Resume",
                "file": large_file,
            },
            format="multipart",
        )

        assert response.status_code == 400

    def test_resume_endpoints_require_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        assert response.status_code == 401
