from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'middle_name', 'last_name', 'avatar')}),
        (_('Permissions'), {'fields': ('role', 'theme', 'is_active', 'is_archived', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'password_changed_at', 'archived_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'middle_name', 'last_name', 'role'),
        }),
    )
    list_display = (
        'avatar_thumbnail',
        'email',
        'first_name', 'middle_name', 'last_name',
        'role', 'is_active', 'is_archived', 'archived_at'
    )
    list_filter = ('role', 'is_active', 'is_archived', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('archived_at', 'password_changed_at')

    def avatar_thumbnail(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" '
                    'style="width: 18px; height: 18px; '
                    'object-fit: cover; '
                    'border-radius: 4px;"'
                ' />',
                obj.avatar.url
            )
        return "—"
    avatar_thumbnail.short_description = _('Avatar')
