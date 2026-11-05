from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Role, Permission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'module', 'description']

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permissions', 'permission_ids', 'created_at']

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        if permission_ids:
            role.permissions.set(permission_ids)
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permission_ids is not None:
            instance.permissions.set(permission_ids)
        return instance

class UserSerializer(serializers.ModelSerializer):
    role_detail = RoleSerializer(source='role', read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'status', 'status_display',
                  'role', 'role_id', 'role_detail', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        role_id = validated_data.pop('role_id', None)
        user = User.objects.create_user(**validated_data)
        if role_id:
            user.role_id = role_id
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        role_id = validated_data.pop('role_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        if role_id is not None:
            instance.role_id = role_id
        instance.save()
        return instance

class UserListSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True, default='')
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'status', 'status_display',
                  'role', 'role_name', 'is_active', 'date_joined']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        if user.status != 1:
            raise serializers.ValidationError('账号已被禁用')
        attrs['user'] = user
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码不正确')
        return value
