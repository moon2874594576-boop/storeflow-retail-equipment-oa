from django.contrib import admin
from .models import Department, Position, Employee

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'manager', 'sort']
    list_filter = ['parent']
    search_fields = ['name', 'code']

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'description']
    search_fields = ['name', 'code']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_no', 'name', 'gender', 'department', 'position', 'status']
    list_filter = ['gender', 'status', 'department']
    search_fields = ['employee_no', 'name', 'phone', 'email']
