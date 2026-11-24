
from django.contrib import admin
from django.urls import include, path

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)



class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({
            "status": "success",
            "message": "API is running",
        })


urlpatterns = [
    path("admin/", admin.site.urls),

    # Public health check
    path("api/health/", HealthCheckView.as_view(), name="health-check"),

    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    path(
    "api/v1/",
    include("apps.applications.urls"),
    ),

    # User authentication and profile APIs
    path("api/v1/", include("apps.users.urls")),
]
