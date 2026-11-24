from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.applications.views import (
    CompanyListCreateView,
    JobApplicationViewSet,
)


router = DefaultRouter()
router.register(
    r"applications",
    JobApplicationViewSet,
    basename="applications",
)

urlpatterns = [
    path("companies/", CompanyListCreateView.as_view(), name="company-list"),
    path("", include(router.urls)),
]