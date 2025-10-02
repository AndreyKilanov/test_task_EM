from django.core.management.base import BaseCommand
from django.db import transaction
from users.models.access_control import Permission, RolePermission
from users.entities import UserRole, Resource, Action


class Command(BaseCommand):
    help = "Initialize default roles and permissions for access control system"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Initializing access control permissions...")

        permissions_data = [
            (Resource.DOCUMENTS, Action.READ),
            (Resource.DOCUMENTS, Action.WRITE),
            (Resource.REPORTS, Action.READ),
            (Resource.USERS, Action.MANAGE),
        ]

        permission_objects = {}
        for resource, action in permissions_data:
            perm, created = Permission.objects.get_or_create(
                resource=str(resource),
                action=str(action),
                defaults={"resource": str(resource), "action": str(action)}
            )
            permission_objects[(resource, action)] = perm
            if created:
                self.stdout.write(f"  ✓ Created permission: {action} on {resource}")

        role_permissions_map = {
            UserRole.ADMIN: [
                (Resource.DOCUMENTS, Action.READ),
                (Resource.DOCUMENTS, Action.WRITE),
                (Resource.REPORTS, Action.READ),
                (Resource.USERS, Action.MANAGE),
            ],
            UserRole.MODERATOR: [
                (Resource.DOCUMENTS, Action.READ),
                (Resource.DOCUMENTS, Action.WRITE),
                (Resource.REPORTS, Action.READ),
            ],
            UserRole.CREATOR: [
                (Resource.DOCUMENTS, Action.READ),
            ],
            UserRole.USER: [
                (Resource.DOCUMENTS, Action.READ),
            ],
        }

        for role, perms in role_permissions_map.items():
            for resource, action in perms:
                perm = permission_objects[(resource, action)]
                _, created = RolePermission.objects.get_or_create(
                    role=role,
                    permission=perm
                )
                if created:
                    self.stdout.write(f"  ✓ Assigned {role} → {action} on {resource}")

        self.stdout.write(
            self.style.SUCCESS("Access control system initialized successfully!")
        )