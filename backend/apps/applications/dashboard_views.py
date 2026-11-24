from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.dashboard_services import (
    get_dashboard_summary,
    get_status_distribution,
    get_employment_type_distribution,
    get_monthly_application_trends,
)
from apps.applications.models import ApplicationNotification


class DashboardSummaryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_dashboard_summary(request.user)

        data["unread_notifications"] = (
            ApplicationNotification.objects
            .filter(
                user=request.user,
                is_read=False,
            )
            .count()
        )

        return Response({
            "success": True,
            "message": "Dashboard summary retrieved successfully.",
            "data": data,
        })


class DashboardTrendsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_monthly_application_trends(
            request.user,
            months=6,
        )

        return Response({
            "success": True,
            "message": "Application trends retrieved successfully.",
            "data": data,
        })


class DashboardDistributionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "success": True,
            "message": "Application distributions retrieved successfully.",
            "data": {
                "status_distribution": get_status_distribution(
                    request.user
                ),
                "employment_type_distribution": (
                    get_employment_type_distribution(request.user)
                ),
            },
        })