import csv
from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.dashboard_services import (
    get_advanced_analytics,
    get_analytics_export_queryset,
)

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

def get_analytics_parameters(request):
    today = timezone.localdate()

    default_start = today - timedelta(days=29)

    start_raw = request.query_params.get("start_date")
    end_raw = request.query_params.get("end_date")

    start_date = (
        parse_date(start_raw) if start_raw else default_start
    )
    end_date = (
        parse_date(end_raw) if end_raw else today
    )

    if start_date is None:
        return None, None, None, Response({
            "success": False,
            "message": "Invalid start_date. Use YYYY-MM-DD.",
            "data": None,
        }, status=status.HTTP_400_BAD_REQUEST)

    if end_date is None:
        return None, None, None, Response({
            "success": False,
            "message": "Invalid end_date. Use YYYY-MM-DD.",
            "data": None,
        }, status=status.HTTP_400_BAD_REQUEST)

    if start_date > end_date:
        return None, None, None, Response({
            "success": False,
            "message": "start_date cannot be after end_date.",
            "data": None,
        }, status=status.HTTP_400_BAD_REQUEST)

    granularity = request.query_params.get(
        "granularity", "weekly"
    ).lower()

    if granularity not in ["daily", "weekly", "monthly"]:
        return None, None, None, Response({
            "success": False,
            "message": (
                "granularity must be daily, weekly or monthly."
            ),
            "data": None,
        }, status=status.HTTP_400_BAD_REQUEST)

    return start_date, end_date, granularity, None


class AdvancedAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date, end_date, granularity, error = (
            get_analytics_parameters(request)
        )

        if error:
            return error

        data = get_advanced_analytics(
            user=request.user,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
        )

        return Response({
            "success": True,
            "message": "Advanced analytics retrieved successfully.",
            "data": data,
        })


class AnalyticsCSVExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date, end_date, _, error = (
            get_analytics_parameters(request)
        )

        if error:
            return error

        applications = get_analytics_export_queryset(
            user=request.user,
            start_date=start_date,
            end_date=end_date,
        )

        response = HttpResponse(
            content_type="text/csv; charset=utf-8"
        )
        response["Content-Disposition"] = (
            'attachment; filename="job_application_report.csv"'
        )

        writer = csv.writer(response)

        writer.writerow([
            "Application ID",
            "Company",
            "Job Title",
            "Status",
            "Employment Type",
            "Work Mode",
            "Location",
            "Salary Minimum",
            "Salary Maximum",
            "Applied Date",
            "Deadline",
            "Job URL",
        ])

        for application in applications:
            writer.writerow([
                application.id,
                application.company.name,
                application.job_title,
                application.status,
                application.employment_type,
                application.work_mode,
                application.location,
                application.salary_min,
                application.salary_max,
                application.applied_date,
                application.deadline,
                application.job_url,
            ])

        return response