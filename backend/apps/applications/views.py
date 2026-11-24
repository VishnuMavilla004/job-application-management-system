
import logging

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.applications.models import (
    JobApplication,
    ApplicationStatusHistory,
)
from apps.applications.permissions import IsApplicationOwner
from apps.applications.serializers import (
    JobApplicationSerializer,
    ApplicationStatusHistorySerializer,
)
from apps.companies.models import Company
from apps.companies.serializers import CompanySerializer


logger = logging.getLogger(__name__)


class CompanyListCreateView(ListCreateAPIView):
    """
    List existing companies and create new companies.
    Companies are shared reference data.
    """

    queryset = Company.objects.all().order_by("name")
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, IsApplicationOwner]

    def get_queryset(self):
        return (
            JobApplication.objects
            .filter(user=self.request.user)
            .select_related("user", "company")
            .prefetch_related("status_history")
            .order_by("-created_at")
        )

    @transaction.atomic
    def perform_create(self, serializer):
        application = serializer.save(user=self.request.user)

        ApplicationStatusHistory.objects.create(
            application=application,
            old_status=None,
            new_status=application.status,
            changed_by=self.request.user,
            remarks="Application created.",
        )

        logger.info(
            "Application %s created by user %s",
            application.id,
            self.request.user.id,
        )

    @transaction.atomic
    def perform_update(self, serializer):
        application = self.get_object()
        old_status = application.status

        updated_application = serializer.save()

        if old_status != updated_application.status:
            ApplicationStatusHistory.objects.create(
                application=updated_application,
                old_status=old_status,
                new_status=updated_application.status,
                changed_by=self.request.user,
                remarks="Application status updated.",
            )

        logger.info(
            "Application %s updated by user %s",
            updated_application.id,
            self.request.user.id,
        )

    def perform_destroy(self, instance):
        logger.info(
            "Application %s deleted by user %s",
            instance.id,
            self.request.user.id,
        )
        instance.delete()

    @action(
        detail=True,
        methods=["get"],
        url_path="history",
        permission_classes=[IsAuthenticated, IsApplicationOwner],
    )
    def history(self, request, pk=None):
        application = self.get_object()

        history = (
            ApplicationStatusHistory.objects
            .filter(application=application)
            .select_related("changed_by")
            .order_by("-changed_at")
        )

        serializer = ApplicationStatusHistorySerializer(
            history,
            many=True,
        )

        return Response(
            {
                "success": True,
                "message": "Application history retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
