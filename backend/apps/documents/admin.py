from django.contrib import admin
from .models import ResumeDocument


@admin.register(ResumeDocument)
class ResumeDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "user",
        "is_default",
        "uploaded_at",
    )

    list_filter = (
        "is_default",
    )

    search_fields = (
        "title",
        "user__email",
    )