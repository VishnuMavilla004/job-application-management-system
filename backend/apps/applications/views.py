
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

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.applications.filters import JobApplicationFilter
from apps.applications.pagination import ApplicationPagination

from apps.applications.serializers import (
    JobApplicationSerializer,
    ApplicationStatusHistorySerializer,
    ApplicationStatusUpdateSerializer,
)

from apps.applications.services import (
    record_status_change,
    change_application_status,
)

from apps.applications.notification_services import (
    notify_application_created,
    notify_application_status_changed,
)

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

    permission_classes = [
        IsAuthenticated,
        IsApplicationOwner,
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = JobApplicationFilter

    search_fields = [
    "job_title",
    "location",
    "company__name",
    "contact_person",
    "contact_email",
    ]

    ordering_fields = [
        "job_title",
        "applied_date",
        "deadline",
        "salary_min",
        "salary_max",
        "status",
        "created_at",
        "updated_at",
        "company__name",
    ]

    ordering = ["-created_at"]

    pagination_class = ApplicationPagination

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

        notify_application_created(application)

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
            remarks = self.request.data.get(
                "remarks",
                "Application status updated.",
            )

            record_status_change(
                application=updated_application,
                old_status=old_status,
                new_status=updated_application.status,
                changed_by=self.request.user,
                remarks=remarks,
            )

            notify_application_status_changed(
                updated_application,
                old_status,
                updated_application.status,
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
        permission_classes=[
            IsAuthenticated,
            IsApplicationOwner,
        ],
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

    
    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
        permission_classes=[
            IsAuthenticated,
            IsApplicationOwner,
        ],
    )
    @transaction.atomic
    def update_status(self, request, pk=None):
        application = self.get_object()

        serializer = ApplicationStatusUpdateSerializer(
            data=request.data,
            context={
                "application": application,
                "request": request,
            },
        )
        serializer.is_valid(raise_exception=True)

        history = change_application_status(
            application=application,
            new_status=serializer.validated_data["status"],
            changed_by=request.user,
            remarks=serializer.validated_data.get("remarks", ""),
        )
        notify_application_status_changed(
            application,
            history.old_status,
            history.new_status,
        )

        application.refresh_from_db()

        return Response(
            {
                "success": True,
                "message": "Application status updated successfully.",
                "data": {
                    "application_id": application.id,
                    "old_status": history.old_status,
                    "new_status": history.new_status,
                    "remarks": history.remarks,
                    "changed_at": history.changed_at,
                },
            },
            status=status.HTTP_200_OK,
        )
