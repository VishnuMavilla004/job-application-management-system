from rest_framework.permissions import BasePermission


class IsApplicationOwner(BasePermission):
    """
    Allow access only to the user who owns the application.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id