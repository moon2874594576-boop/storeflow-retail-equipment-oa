from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Department, Position, Employee
from .serializers import (
    DepartmentSerializer, DepartmentListSerializer,
    PositionSerializer, EmployeeSerializer, EmployeeListSerializer
)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related('parent', 'manager').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return DepartmentListSerializer
        return DepartmentSerializer

    def get_queryset(self):
        queryset = Department.objects.select_related('parent', 'manager').all()
        keyword = self.request.query_params.get('keyword', '')
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | Q(code__icontains=keyword)
            )
        return queryset

    @action(detail=False, methods=['get'])
    def tree(self, request):
        departments = Department.objects.filter(parent=None).order_by('sort')
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def all(self, request):
        departments = Department.objects.all().order_by('sort')
        serializer = DepartmentListSerializer(departments, many=True)
        return Response(serializer.data)

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Position.objects.all()
        keyword = self.request.query_params.get('keyword', '')
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | Q(code__icontains=keyword)
            )
        return queryset

    @action(detail=False, methods=['get'])
    def all(self, request):
        positions = Position.objects.all().order_by('name')
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('department', 'position', 'user').all()
    filterset_fields = ['gender', 'status', 'department', 'position']
    search_fields = ['employee_no', 'name', 'phone', 'email']
    ordering_fields = ['employee_no', 'name', 'created_at']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeSerializer

    def get_queryset(self):
        queryset = Employee.objects.select_related('department', 'position', 'user').all()
        keyword = self.request.query_params.get('keyword', '')
        if keyword:
            queryset = queryset.filter(
                Q(employee_no__icontains=keyword) |
                Q(name__icontains=keyword) |
                Q(phone__icontains=keyword) |
                Q(email__icontains=keyword)
            )
        return queryset

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '请选择要删除的员工'}, status=status.HTTP_400_BAD_REQUEST)
        Employee.objects.filter(id__in=ids).delete()
        return Response({'message': '删除成功'})
