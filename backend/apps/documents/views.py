
import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.text import get_valid_filename

from rest_framework import status
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.models import ResumeDocument
from apps.documents.serializers import ResumeDocumentSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


def api_response(data=None, message="", status_code=status.HTTP_200_OK):
    return Response(
        {
            "success": status_code < 400,
            "message": message,
            "data": data,
        },
        status=status_code,
    )


def lock_user(user_id):
    return User.objects.select_for_update().get(pk=user_id)


def set_default_resume(user_id, resume_id):
    """
    Lock the owner row to serialize default-resume changes.
    The database constraint remains the final integrity safeguard.
    """
    with transaction.atomic():
        lock_user(user_id)

        resume = get_object_or_404(
            ResumeDocument.objects.select_for_update(),
            pk=resume_id,
            user_id=user_id,
        )

        ResumeDocument.objects.filter(
            user_id=user_id,
            is_default=True,
        ).exclude(pk=resume.pk).update(is_default=False)

        if not resume.is_default:
            resume.is_default = True
            resume.save(update_fields=["is_default"])

        return resume


class ResumeListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        resumes = ResumeDocument.objects.filter(
            user=request.user
        ).order_by("-uploaded_at")

        serializer = ResumeDocumentSerializer(
            resumes,
            many=True,
            context={"request": request},
        )

        return api_response(
            serializer.data,
            "Resumes retrieved successfully.",
        )

    def post(self, request):
        serializer = ResumeDocumentSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                lock_user(request.user.pk)

                make_default = serializer.validated_data.get(
                    "is_default", False
                )

                if make_default:
                    ResumeDocument.objects.filter(
                        user=request.user,
                        is_default=True,
                    ).update(is_default=False)

                resume = serializer.save(user=request.user)

        except Exception:
            logger.exception("Resume upload failed.")
            raise

        return api_response(
            ResumeDocumentSerializer(
                resume,
                context={"request": request},
            ).data,
            "Resume uploaded successfully.",
            status.HTTP_201_CREATED,
        )


class ResumeDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return ResumeDocument.objects.filter(user=self.request.user)

    def get_object(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)

    def get(self, request, pk):
        resume = self.get_object(pk)

        return api_response(
            ResumeDocumentSerializer(
                resume,
                context={"request": request},
            ).data,
            "Resume retrieved successfully.",
        )

    def patch(self, request, pk):
        old_file_name = None

        with transaction.atomic():
            lock_user(request.user.pk)

            resume = get_object_or_404(
                ResumeDocument.objects.select_for_update(),
                pk=pk,
                user=request.user,
            )

            serializer = ResumeDocumentSerializer(
                resume,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)

            if "file" in serializer.validated_data and resume.file:
                old_file_name = resume.file.name

            make_default = serializer.validated_data.get(
                "is_default", False
            )

            if make_default:
                ResumeDocument.objects.filter(
                    user=request.user,
                    is_default=True,
                ).exclude(pk=resume.pk).update(is_default=False)

            updated_resume = serializer.save()

            if (
                old_file_name
                and updated_resume.file
                and old_file_name != updated_resume.file.name
            ):
                storage = resume.file.storage
                transaction.on_commit(
                    lambda: storage.delete(old_file_name)
                )

        return api_response(
            ResumeDocumentSerializer(
                updated_resume,
                context={"request": request},
            ).data,
            "Resume updated successfully.",
        )

    def delete(self, request, pk):
        with transaction.atomic():
            lock_user(request.user.pk)

            resume = get_object_or_404(
                ResumeDocument.objects.select_for_update(),
                pk=pk,
                user=request.user,
            )

            old_file_name = resume.file.name if resume.file else None
            storage = resume.file.storage if resume.file else None
            was_default = resume.is_default

            resume.delete()

            if was_default:
                replacement = (
                    ResumeDocument.objects
                    .filter(user=request.user)
                    .order_by("-uploaded_at")
                    .first()
                )

                if replacement:
                    replacement.is_default = True
                    replacement.save(update_fields=["is_default"])

            if old_file_name and storage:
                transaction.on_commit(
                    lambda: storage.delete(old_file_name)
                )

        return api_response(
            message="Resume deleted successfully.",
        )


class ResumeSetDefaultView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        resume = set_default_resume(request.user.pk, pk)

        return api_response(
            ResumeDocumentSerializer(
                resume,
                context={"request": request},
            ).data,
            "Default resume updated successfully.",
        )


class ResumeDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        resume = get_object_or_404(
            ResumeDocument.objects.filter(user=request.user),
            pk=pk,
        )

        if not resume.file:
            return api_response(
                message="Resume file not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        filename = get_valid_filename(resume.file.name.split("/")[-1])

        try:
            return FileResponse(
                resume.file.open("rb"),
                as_attachment=True,
                filename=filename,
            )
        except (FileNotFoundError, OSError):
            logger.exception("Unable to open resume file %s", resume.pk)

            return api_response(
                message="Resume file is unavailable.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
