
from django.contrib import admin
from django.urls import path

from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        "status": "success",
        "message": "Job Application Management API is running",
        "version": "1.0.0",
    })


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/health/", health_check),

    path(
        "api/schema/",
        SpectacularAPIView.as_view(
            permission_classes=[AllowAny]
        ),
        name="schema",
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            permission_classes=[AllowAny],
        ),
        name="swagger-ui",
    ),
]
