
from django.urls import path

from apps.documents.views import (
    ResumeListCreateView,
    ResumeDetailView,
    ResumeSetDefaultView,
    ResumeDownloadView,
)

urlpatterns = [
    path(
        "resumes/",
        ResumeListCreateView.as_view(),
        name="resume-list-create",
    ),
    path(
        "resumes/<int:pk>/",
        ResumeDetailView.as_view(),
        name="resume-detail",
    ),
    path(
        "resumes/<int:pk>/default/",
        ResumeSetDefaultView.as_view(),
        name="resume-set-default",
    ),
    path(
        "resumes/<int:pk>/download/",
        ResumeDownloadView.as_view(),
        name="resume-download",
    ),
]
