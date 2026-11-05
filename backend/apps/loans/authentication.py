from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import get_md5_hash_password
from apps.users.models import User


class ActiveJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not user.is_active or user.status != 1:
            raise AuthenticationFailed('账号已停用，请联系系统管理员。')
        return user


class ActiveTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = self.token_class(attrs['refresh'])
        try:
            user = User.objects.get(pk=refresh[api_settings.USER_ID_CLAIM])
        except (User.DoesNotExist, KeyError):
            raise AuthenticationFailed('账号不存在或已停用。')
        if not user.is_active or user.status != 1:
            raise AuthenticationFailed('账号已停用。')
        if refresh.get(api_settings.REVOKE_TOKEN_CLAIM) != get_md5_hash_password(user.password):
            raise AuthenticationFailed('密码已变化，请重新登录。')
        return super().validate(attrs)
