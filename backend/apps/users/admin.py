from django.contrib import admin
from .models import User, Role, Permission

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'role', 'status', 'is_staff']
    list_filter = ['status', 'role']
    search_fields = ['username', 'email', 'phone']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description', 'created_at']

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'module', 'description']
    list_filter = ['module']
