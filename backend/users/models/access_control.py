from django.db import models
from django.utils.translation import gettext_lazy as _
from users.entities import UserRole, Action, Resource


class Permission(models.Model):
    """
    Represents a permission to perform an action on a resource.
    """
    RESOURCE_CHOICES = Resource.choices()
    ACTION_CHOICES = Action.choices()

    resource = models.CharField(
        max_length=200,
        choices=RESOURCE_CHOICES,
        verbose_name=_('resource')
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name=_('action')
    )

    class Meta:
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        unique_together = ('resource', 'action')
        ordering = ['resource', 'action']

    def __str__(self):
        return f"{self.action} → {self.resource}"


class RolePermission(models.Model):
    """
    Maps a UserRole (from enum) to a Permission.
    This allows dynamic permission assignment per role.
    """
    role = models.CharField(
        max_length=50,
        choices=[role.to_tuple() for role in UserRole],
        verbose_name=_('role'),
        help_text=_('Role from the system enum')
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_mappings',
        verbose_name=_('permission')
    )

    class Meta:
        verbose_name = _('role permission mapping')
        verbose_name_plural = _('role permission mappings')
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.get_role_display()} → {self.permission}"
