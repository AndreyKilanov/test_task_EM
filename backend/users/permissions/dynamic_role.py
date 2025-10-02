from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from users.models import RolePermission, Permission


class DynamicRolePermission(BasePermission):
    """
    Checks if the user's role (from CustomUser.role) has permission
    to perform the requested action on the resource.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if getattr(user, 'is_archived', False):
            return False

        path = request.path.strip('/')
        method = request.method

        action_map = {
            'GET': 'read',
            'POST': 'write',
            'PUT': 'write',
            'PATCH': 'write',
            'DELETE': 'delete',
        }
        action = action_map.get(method, 'read')

        try:
            permission = Permission.objects.get(resource=path, action=action)
        except Permission.DoesNotExist:
            return False

        has_access = RolePermission.objects.filter(
            role=user.role,
            permission=permission
        ).exists()

        if not has_access:
            raise PermissionDenied("You don't have the rights to perform this action.")

        return True