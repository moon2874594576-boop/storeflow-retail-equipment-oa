from rest_framework import serializers
from .models import Department, Position, Employee

class DepartmentSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True, default='')
    manager_name = serializers.CharField(source='manager.username', read_only=True, default='')
    children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'parent', 'parent_name', 'manager', 'manager_name',
                  'sort', 'children', 'created_at']
        read_only_fields = ['created_at']

    def get_children(self, obj):
        children = Department.objects.filter(parent=obj)
        return DepartmentSerializer(children, many=True).data

class DepartmentListSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True, default='')
    manager_name = serializers.CharField(source='manager.username', read_only=True, default='')

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'parent', 'parent_name', 'manager', 'manager_name', 'sort']

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name', 'code', 'description']

class EmployeeSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default='')
    position_name = serializers.CharField(source='position.name', read_only=True, default='')
    user_name = serializers.CharField(source='user.username', read_only=True, default='')

    class Meta:
        model = Employee
        fields = ['id', 'employee_no', 'name', 'gender', 'gender_display', 'id_card',
                  'phone', 'email', 'department', 'department_name',
                  'position', 'position_name', 'entry_date', 'status', 'status_display',
                  'user', 'user_name', 'created_at']
        read_only_fields = ['created_at']

class EmployeeListSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default='')
    position_name = serializers.CharField(source='position.name', read_only=True, default='')

    class Meta:
        model = Employee
        fields = ['id', 'employee_no', 'name', 'gender', 'gender_display',
                  'phone', 'email', 'department', 'department_name',
                  'position', 'position_name', 'status', 'status_display']
