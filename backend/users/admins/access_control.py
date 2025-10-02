from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from users.models import Permission, RolePermission
from users.entities import UserRole


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('resource', 'action',)
    list_filter = ('resource', 'action')
    search_fields = ('resource', 'action')
    ordering = ('resource', 'action')


class UserRoleFilter(admin.SimpleListFilter):
    title = _('role')
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return [(role.value, role.to_tuple()[1]) for role in UserRole]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(role=self.value())
        return queryset


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role_display', 'permission_resource', 'permission_action')
    list_filter = (UserRoleFilter, 'permission__resource', 'permission__action')
    search_fields = ('permission__resource',)
    ordering = ('role', 'permission__resource')

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "role":
            kwargs['choices'] = [(role.value, role.to_tuple()[1]) for role in UserRole]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def role_display(self, obj):
        role_enum = next((r for r in UserRole if r.value == obj.role), None)
        return role_enum.to_tuple()[1] if role_enum else obj.role
    role_display.short_description = _('Role')
    role_display.admin_order_field = 'role'

    def permission_resource(self, obj):
        return obj.permission.get_resource_display()
    permission_resource.short_description = _('Resource')

    def permission_action(self, obj):
        return obj.permission.get_action_display()
    permission_action.short_description = _('Action')
