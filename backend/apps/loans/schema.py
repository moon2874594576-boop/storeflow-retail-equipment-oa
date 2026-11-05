"""Executable OpenAPI descriptions, shared with the actual serializers."""
from rest_framework import serializers
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import StoreSerializer, AssetSerializer, LoanSerializer, LoanDetailSerializer, LoanInputSerializer, EventSerializer


class StoreFlowJWTDocumentation(OpenApiAuthenticationExtension):
    target_class = 'apps.loans.authentication.ActiveJWTAuthentication'
    name = 'jwtAuth'

    def get_security_definition(self, auto_schema):
        return {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT', 'description': '登录获得 access token；账号停用后现有 token 也不能访问业务接口。'}


class UserResponse(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    display_name = serializers.CharField()
    role = serializers.ChoiceField(choices=['employee', 'manager', 'custodian', 'admin'])
    store_id = serializers.IntegerField(allow_null=True)
    store_name = serializers.CharField()
    status = serializers.IntegerField()
    email = serializers.EmailField()


class AccountWrite(serializers.Serializer):
    username = serializers.CharField(required=False, max_length=50)
    display_name = serializers.CharField(required=False, max_length=80)
    role = serializers.ChoiceField(choices=['employee', 'manager', 'custodian', 'admin'], required=False)
    store_id = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.IntegerField(required=False, min_value=0, max_value=1)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False, write_only=True, min_length=10)


Error = inline_serializer('APIError', fields={'detail': serializers.CharField(help_text='校验失败时也可能返回字段到错误列表的映射。')})
Reason = inline_serializer('ActionReason', fields={'reason': serializers.CharField(max_length=1000)})
OptionalReason = inline_serializer('OptionalReason', fields={'reason': serializers.CharField(max_length=1000, required=False, allow_blank=True)})
Health = inline_serializer('HealthResponse', fields={'status': serializers.ChoiceField(choices=['ok', 'not_ready']), 'version': serializers.CharField(), 'database': serializers.CharField(), 'demo_mode': serializers.BooleanField()})
PK = OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH, required=True)
PK_ALT = OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, required=True)
filters = [OpenApiParameter('q', str, description='按申请编号、用途、账号或设备编号搜索'), OpenApiParameter('status', str), OpenApiParameter('category_id', int), OpenApiParameter('store_id', int), OpenApiParameter('overdue', bool)]


def document_api(namespace):
    namespace['LoginView'].post = extend_schema(
        request=inline_serializer('LoginRequest', fields={'username': serializers.CharField(), 'password': serializers.CharField(write_only=True)}),
        responses={200: inline_serializer('LoginResponse', fields={'access': serializers.CharField(), 'refresh': serializers.CharField(), 'user': UserResponse()}), 401: Error}, auth=[], tags=['认证']
    )(namespace['LoginView'].post)
    namespace['MeView'].get = extend_schema(responses=UserResponse, tags=['认证'])(namespace['MeView'].get)
    namespace['MeView'].patch = extend_schema(request=inline_serializer('ProfileUpdate', fields={'display_name': serializers.CharField(max_length=80)}), responses=UserResponse, tags=['认证'])(namespace['MeView'].patch)
    namespace['PasswordView'].post = extend_schema(request=inline_serializer('ChangePassword', fields={'old_password': serializers.CharField(write_only=True), 'new_password': serializers.CharField(write_only=True, min_length=10)}), responses=Error, tags=['认证'])(namespace['PasswordView'].post)
    namespace['CategoryView'].get = extend_schema(responses=inline_serializer('Category', fields={'id': serializers.IntegerField(), 'name': serializers.CharField(), 'code': serializers.CharField()}, many=True), tags=['基础资料'])(namespace['CategoryView'].get)
    namespace['StoreViewSet'] = extend_schema_view(
        list=extend_schema(responses=StoreSerializer(many=True), tags=['门店']),
        create=extend_schema(request=StoreSerializer, responses={201: StoreSerializer}, description='仅系统管理员；先创建门店，再创建关联店长账号，最后更新 manager_id。', tags=['门店']),
        partial_update=extend_schema(parameters=[PK], request=StoreSerializer(partial=True), responses=StoreSerializer, tags=['门店'])
    )(namespace['StoreViewSet'])
    namespace['AssetViewSet'] = extend_schema_view(
        list=extend_schema(parameters=[OpenApiParameter('q', str), OpenApiParameter('status', str), OpenApiParameter('category_id', int)], responses=AssetSerializer(many=True), tags=['设备']),
        retrieve=extend_schema(parameters=[PK], responses=AssetSerializer, tags=['设备']),
        create=extend_schema(request=AssetSerializer, responses={201: AssetSerializer}, tags=['设备']),
        partial_update=extend_schema(parameters=[PK], request=AssetSerializer(partial=True), responses=AssetSerializer, tags=['设备']),
        repair=extend_schema(parameters=[PK], request=Reason, responses=AssetSerializer, tags=['设备'])
    )(namespace['AssetViewSet'])
    namespace['LoanViewSet'] = extend_schema_view(
        list=extend_schema(parameters=filters, responses=LoanSerializer(many=True), tags=['借用']),
        retrieve=extend_schema(parameters=[PK], responses=LoanDetailSerializer, tags=['借用']),
        create=extend_schema(request=LoanInputSerializer, responses={201: LoanDetailSerializer}, tags=['借用']),
        partial_update=extend_schema(parameters=[PK], request=LoanInputSerializer(partial=True), responses=LoanDetailSerializer, tags=['借用']),
        export=extend_schema(parameters=filters, responses={(200, 'text/csv'): OpenApiResponse(response=OpenApiTypes.STR, description='UTF-8 BOM CSV，使用与列表相同的数据权限，并转义公式单元格。')}, tags=['借用'])
    )(namespace['LoanViewSet'])
    action_inputs = {
        'submit': None, 'approve': OptionalReason, 'reject': Reason, 'withdraw': OptionalReason,
        'issue': inline_serializer('IssueDevice', fields={'asset_id': serializers.IntegerField(), 'reason': serializers.CharField(required=False)}),
        'undo_issue': Reason, 'receive': None, 'return_device': OptionalReason,
        'inspect': inline_serializer('Inspection', fields={'condition': serializers.ChoiceField(choices=['normal', 'damaged']), 'reason': serializers.CharField(required=False, help_text='damaged 时必填。')}),
    }
    for name, body in action_inputs.items():
        method = getattr(namespace['LoanViewSet'], name)
        setattr(namespace['LoanViewSet'], name, extend_schema(parameters=[PK], request=body, responses={200: LoanDetailSerializer, 400: Error, 403: Error, 409: Error}, tags=['借用流转'])(method))
    namespace['DashboardView'].get = extend_schema(responses=inline_serializer('Dashboard', fields={
        'metrics': inline_serializer('Metrics', fields={'pending': serializers.IntegerField(), 'active': serializers.IntegerField(), 'overdue': serializers.IntegerField(), 'available': serializers.IntegerField(), 'inspection': serializers.IntegerField(), 'avg_approval_hours': serializers.FloatField(), 'total': serializers.IntegerField()}),
        'by_status': inline_serializer('StatusCount', fields={'name': serializers.CharField(), 'status': serializers.CharField(), 'value': serializers.IntegerField()}, many=True),
        'recent': LoanSerializer(many=True), 'trend': inline_serializer('DailyCount', fields={'date': serializers.DateField(), 'count': serializers.IntegerField()}, many=True)
    }), tags=['统计'])(namespace['DashboardView'].get)
    namespace['AuditViewSet'].serializer_class = EventSerializer
    namespace['AuditViewSet'].list = extend_schema(responses=EventSerializer(many=True), tags=['审计'])(namespace['AuditViewSet'].list)
    namespace['AccountViewSet'].serializer_class = UserResponse
    namespace['AccountViewSet'] = extend_schema_view(
        list=extend_schema(parameters=[OpenApiParameter('q', str)], responses=UserResponse(many=True), tags=['账号']),
        create=extend_schema(request=AccountWrite, responses={201: UserResponse}, tags=['账号']),
        partial_update=extend_schema(parameters=[PK], request=AccountWrite(partial=True), responses=UserResponse, tags=['账号'])
    )(namespace['AccountViewSet'])
    namespace['health'] = extend_schema(responses={200: Health, 503: Health}, auth=[], tags=['运行状态'])(namespace['health'])
