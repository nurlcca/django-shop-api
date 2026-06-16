from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return False

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )