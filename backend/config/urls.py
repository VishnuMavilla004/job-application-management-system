
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({
        "status": "success",
        "message": "Job Application Management API is running",
        "version": "1.0.0",
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check),
]
