
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.applications.views import (
    CompanyListCreateView,
    JobApplicationViewSet,
)

from apps.applications.dashboard_views import (
    DashboardSummaryView,
    DashboardTrendsView,
    DashboardDistributionView,
)

from apps.applications.notification_views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
)

from apps.applications.dashboard_views import (
    AdvancedAnalyticsView,
    AnalyticsCSVExportView,
)

router = DefaultRouter()
router.register(
    r"applications",
    JobApplicationViewSet,
    basename="applications",
)

urlpatterns = [
    path("companies/", CompanyListCreateView.as_view(), name="company-list"),

    path(
        "dashboard/summary/",
        DashboardSummaryView.as_view(),
        name="dashboard-summary",
    ),
    path(
        "dashboard/trends/",
        DashboardTrendsView.as_view(),
        name="dashboard-trends",
    ),
    path(
        "dashboard/distribution/",
        DashboardDistributionView.as_view(),
        name="dashboard-distribution",
    ),

    path(
        "notifications/",
        NotificationListView.as_view(),
        name="notification-list",
    ),
    path(
        "notifications/<int:pk>/read/",
        NotificationMarkReadView.as_view(),
        name="notification-mark-read",
    ),
    path(
        "notifications/read-all/",
        NotificationMarkAllReadView.as_view(),
        name="notification-mark-all-read",
    ),

    path(
    "dashboard/analytics/",
    AdvancedAnalyticsView.as_view(),
    name="dashboard-advanced-analytics",
    ),
    path(
        "dashboard/analytics/export/",
        AnalyticsCSVExportView.as_view(),
        name="dashboard-analytics-export",
    ),

    path("", include(router.urls)),
]