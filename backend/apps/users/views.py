from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from .models import User, Role, Permission
from .serializers import (
    UserSerializer, UserListSerializer, LoginSerializer,
    UserProfileSerializer, ChangePasswordSerializer,
    RoleSerializer, PermissionSerializer
)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data
        })

    @action(detail=False, methods=['get'])
    def profile(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        user = request.user
        data = request.data.copy()
        if 'role_id' in data:
            data.pop('role_id')
        serializer = UserProfileSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': '密码修改成功'})

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filterset_fields = ['status', 'role']
    search_fields = ['username', 'email', 'phone']
    ordering_fields = ['id', 'username', 'date_joined']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = User.objects.select_related('role').all()
        keyword = self.request.query_params.get('keyword', '')
        if keyword:
            queryset = queryset.filter(
                Q(username__icontains=keyword) |
                Q(email__icontains=keyword) |
                Q(phone__icontains=keyword)
            )
        return queryset

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '请选择要删除的用户'}, status=status.HTTP_400_BAD_REQUEST)
        User.objects.filter(id__in=ids).delete()
        return Response({'message': '删除成功'})

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.prefetch_related('permissions').all()
    serializer_class = RoleSerializer

    @action(detail=False, methods=['get'])
    def all(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filterset_fields = ['module']

    @action(detail=False, methods=['get'])
    def all(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
