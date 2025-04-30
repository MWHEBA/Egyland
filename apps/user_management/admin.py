from django.contrib import admin
from .models import Role, UserRole

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'can_manage_users')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_by', 'assigned_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'role__name')
    ordering = ('-assigned_at',)
    raw_id_fields = ('user', 'assigned_by')
