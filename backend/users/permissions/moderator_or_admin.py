from rest_framework import permissions

from users.entities import UserRole


class IsModeratorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in {UserRole.MODERATOR, UserRole.ADMIN}
        )
    