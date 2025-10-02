from rest_framework import permissions

from users.entities import UserRole


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.USER
        )
