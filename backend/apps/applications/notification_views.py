from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.models import ApplicationNotification
from apps.applications.notification_serializers import (
    ApplicationNotificationSerializer,
)


class NotificationPagination(PageNumberPagination):

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "unread_count": self.unread_count,
            "results": data,
        })


class NotificationListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = (
            ApplicationNotification.objects
            .filter(user=request.user)
            .select_related("application")
            .order_by("-created_at")
        )

        paginator = NotificationPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = ApplicationNotificationSerializer(
            page,
            many=True,
        )

        paginator.unread_count = queryset.filter(
            is_read=False
        ).count()

        return paginator.get_paginated_response(serializer.data)


class NotificationMarkReadView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        notification = get_object_or_404(
            ApplicationNotification,
            pk=pk,
            user=request.user,
        )

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response({
            "success": True,
            "message": "Notification marked as read.",
            "data": ApplicationNotificationSerializer(
                notification
            ).data,
        })


class NotificationMarkAllReadView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        updated_count = (
            ApplicationNotification.objects
            .filter(
                user=request.user,
                is_read=False,
            )
            .update(is_read=True)
        )

        return Response({
            "success": True,
            "message": "All notifications marked as read.",
            "data": {
                "updated_count": updated_count,
            },
        }, status=status.HTTP_200_OK)