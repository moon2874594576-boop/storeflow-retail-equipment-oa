import csv
import mimetypes
from collections.abc import Mapping
from datetime import timedelta
from io import StringIO
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import connection, transaction, IntegrityError, OperationalError
from django.db.models import Q, Count
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.exceptions import PermissionDenied, ValidationError, AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User, Role
from .models import Store, Category, Asset, LoanProfile, LoanRequest, LoanEvent
from .serializers import StoreSerializer, AssetSerializer, LoanSerializer, LoanDetailSerializer, LoanInputSerializer, EventSerializer
from .services import role, profile, user_name, scoped_requests, transition, actor_can, Conflict, event


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


def require_role(user, *codes):
    if role(user) not in codes:
        raise PermissionDenied('当前角色无权操作。')


def user_data(user):
    item = profile(user)
    return {'id': user.id, 'username': user.username, 'display_name': user_name(user), 'role': role(user),
            'store_id': item.store_id if item else None, 'store_name': item.store.name if item and item.store_id else '',
            'status': user.status, 'email': user.email}


class ObjectBodyMixin:
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.method in {'POST', 'PATCH', 'PUT'} and not isinstance(request.data, Mapping):
            raise ValidationError('请求体必须为字段对象。')


class LoginView(ObjectBodyMixin, APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        if not isinstance(request.data.get('username'), str) or not isinstance(request.data.get('password'), str):
            raise ValidationError('账号和密码必须为文本。')
        user = authenticate(request, username=request.data.get('username'), password=request.data.get('password'))
        if not user or user.status != 1 or not user.is_active or role(user) not in {'employee', 'manager', 'custodian', 'admin'}:
            raise AuthenticationFailed('账号或密码错误，或账号已停用。')
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'user': user_data(user)})


class MeView(ObjectBodyMixin, APIView):
    def get(self, request):
        return Response(user_data(request.user))

    def patch(self, request):
        if set(request.data) - {'display_name'}:
            raise ValidationError('个人资料只允许修改显示名称。')
        name = str(request.data.get('display_name', '')).strip()
        if not 1 <= len(name) <= 80:
            raise ValidationError({'display_name': '名称长度应为1至80字。'})
        item, _ = LoanProfile.objects.get_or_create(user=request.user)
        item.display_name = name
        item.save()
        return Response(user_data(request.user))


class PasswordView(ObjectBodyMixin, APIView):
    def post(self, request):
        user = request.user
        if not user.check_password(request.data.get('old_password', '')):
            raise ValidationError({'old_password': '原密码不正确。'})
        password = request.data.get('new_password', '')
        if not isinstance(password, str):
            raise ValidationError({'new_password': '密码必须为文本。'})
        try:
            validate_password(password, user)
        except DjangoValidationError as exc:
            raise ValidationError({'new_password': exc.messages})
        user.set_password(password)
        user.save(update_fields=['password'])
        return Response({'detail': '密码已修改，请重新登录。'})


class CategoryView(APIView):
    def get(self, request):
        return Response(list(Category.objects.order_by('id').values('id', 'name', 'code')))


class StoreViewSet(ObjectBodyMixin, viewsets.ViewSet):
    queryset = Store.objects.none()
    def list(self, request):
        qs = Store.objects.select_related('manager__loan_profile').order_by('id')
        if role(request.user) not in {'admin', 'custodian'}:
            item = profile(request.user)
            qs = qs.filter(pk=item.store_id) if item else qs.none()
        return Response(StoreSerializer(qs, many=True).data)

    def create(self, request):
        require_role(request.user, 'admin')
        serializer = StoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.check_manager(serializer.validated_data.get('manager'), None)
        item = serializer.save()
        event(None, request.user, 'store_update', '', '', f'创建门店 {item.code}')
        return Response(StoreSerializer(item).data, status=201)

    def partial_update(self, request, pk=None):
        require_role(request.user, 'admin')
        item = get_object_or_404(Store, pk=pk)
        serializer = StoreSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_manager = serializer.validated_data.get('manager', item.manager)
        if new_manager != item.manager and item.loanrequest_set.filter(status='pending').exists():
            raise ValidationError('门店有待审批申请，请先处理后再更换店长。')
        self.check_manager(new_manager, item.id)
        item = serializer.save()
        event(None, request.user, 'store_update', '', '', f'更新门店 {item.code}')
        return Response(StoreSerializer(item).data)

    @staticmethod
    def check_manager(manager, store_id):
        if manager:
            item = profile(manager)
            if role(manager) != 'manager' or manager.status != 1 or not manager.is_active:
                raise ValidationError({'manager_id': '店长必须是已启用的店长账号。'})
            if not item or item.store_id != store_id:
                raise ValidationError({'manager_id': '店长必须属于该门店。'})


class AssetViewSet(ObjectBodyMixin, viewsets.GenericViewSet):
    serializer_class = AssetSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Asset.objects.none()
        qs = Asset.objects.select_related('category').order_by('code')
        user = self.request.user
        if role(user) in {'employee', 'manager'}:
            visible_ids = scoped_requests(user).filter(status__in=['handover', 'borrowed', 'return_pending']).values_list('asset_id', flat=True)
            qs = qs.filter(Q(status='available') | Q(id__in=visible_ids))
        elif role(user) not in {'admin', 'custodian'}:
            qs = qs.none()
        for key in ['status', 'category_id']:
            value = self.request.query_params.get(key)
            if value:
                if key == 'category_id' and not value.isdigit():
                    raise ValidationError({key: '请选择有效类别。'})
                qs = qs.filter(**{key: value})
        q = self.request.query_params.get('q', '').strip()
        return qs.filter(Q(code__icontains=q) | Q(name__icontains=q) | Q(serial_number__icontains=q)) if q else qs

    def list(self, request):
        page = self.paginate_queryset(self.get_queryset())
        return self.get_paginated_response(self.get_serializer(page, many=True).data)

    def retrieve(self, request, pk=None):
        return Response(self.get_serializer(self.get_object()).data)

    def create(self, request):
        require_role(request.user, 'admin', 'custodian')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            asset = serializer.save()
            event(None, request.user, 'asset_create', '', asset.status, asset.code, asset)
        return Response(self.get_serializer(asset).data, status=201)

    def partial_update(self, request, pk=None):
        require_role(request.user, 'admin', 'custodian')
        asset = self.get_object()
        with transaction.atomic():
            if not Asset.objects.filter(pk=asset.pk, status='available').update(updated_at=timezone.now()):
                raise Conflict('占用或待维修设备不能修改基础资料。')
            asset = Asset.objects.select_for_update().get(pk=asset.pk)
            serializer = self.get_serializer(asset, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            asset = serializer.save()
            event(None, request.user, 'asset_update', asset.status, asset.status, asset.code, asset)
        return Response(self.get_serializer(asset).data)

    @action(detail=True, methods=['post'])
    def repair(self, request, pk=None):
        require_role(request.user, 'custodian')
        asset = self.get_object()
        reason = str(request.data.get('reason', '')).strip()
        if not reason or len(reason) > 1000:
            raise ValidationError({'reason': '请填写1至1000字的修复说明。'})
        with transaction.atomic():
            if not Asset.objects.filter(pk=asset.pk, status='maintenance').update(status='available', updated_at=timezone.now()):
                raise Conflict('该设备不处于待维修状态。')
            event(None, request.user, 'repair', 'maintenance', 'available', reason, asset)
        asset.refresh_from_db()
        return Response(self.get_serializer(asset).data)


class LoanViewSet(ObjectBodyMixin, viewsets.GenericViewSet):
    serializer_class = LoanSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LoanRequest.objects.none()
        qs = scoped_requests(self.request.user)
        for key in ['status', 'category_id', 'store_id']:
            value = self.request.query_params.get(key)
            if value:
                if key.endswith('_id') and not value.isdigit():
                    raise ValidationError({key: '筛选编号无效。'})
                qs = qs.filter(**{key: value})
        if self.request.query_params.get('overdue') in {'1', 'true'}:
            qs = qs.filter(status__in=['borrowed', 'return_pending'], due_date__lt=timezone.localdate())
        q = self.request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(Q(number__icontains=q) | Q(purpose__icontains=q) | Q(applicant__username__icontains=q) | Q(applicant__loan_profile__display_name__icontains=q) | Q(asset__code__icontains=q))
        return qs

    def output(self, item, detail=True):
        cls = LoanDetailSerializer if detail else LoanSerializer
        return cls(item, context={'request': self.request}).data

    def list(self, request):
        page = self.paginate_queryset(self.get_queryset())
        return self.get_paginated_response(LoanSerializer(page, many=True, context={'request': request}).data)

    def retrieve(self, request, pk=None):
        return Response(self.output(self.get_object()))

    def create(self, request):
        require_role(request.user, 'employee')
        item = profile(request.user)
        if not item or not item.store_id:
            raise ValidationError('账号尚未关联门店，请联系管理员。')
        serializer = LoanInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            loan = serializer.save(applicant=request.user, store=item.store)
            event(loan, request.user, 'create', '', 'draft')
        return Response(self.output(loan), status=201)

    def partial_update(self, request, pk=None):
        loan = self.get_object()
        if not actor_can(request.user, loan, 'edit'):
            raise PermissionDenied()
        if loan.status != 'draft':
            raise Conflict('仅草稿可以编辑。')
        serializer = LoanInputSerializer(loan, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            if not LoanRequest.objects.filter(pk=loan.pk, status='draft').update(updated_at=timezone.now()):
                raise Conflict()
            loan = serializer.save()
            event(loan, request.user, 'edit', 'draft', 'draft')
        return Response(self.output(loan))

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        stream = StringIO(newline='')
        writer = csv.writer(stream)
        writer.writerow(['申请编号', '申请人', '门店', '设备类别', '用途', '预计归还', '状态', '设备编号', '是否逾期'])
        for item in self.get_queryset().iterator():
            cells = [item.number, user_name(item.applicant), item.store.name, item.category.name, item.purpose, str(item.due_date), item.get_status_display(), item.asset.code if item.asset_id else '', '是' if item.overdue else '否']
            writer.writerow(["'" + x if str(x).lstrip().startswith(('=', '+', '-', '@', '\t', '\r')) else x for x in cells])
        response = HttpResponse(stream.getvalue().encode('utf-8-sig'), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="storeflow-loans.csv"'
        return response

    def perform_action(self, request, pk, name):
        loan = self.get_object()
        try:
            changed = transition(request.user, loan, name, request.data)
        except (OperationalError, IntegrityError):
            raise Conflict('设备或申请被其他操作更新，请刷新后重试。')
        return Response(self.output(changed))


# 明确的业务动作替代可任意 PATCH 状态的通用审批接口。
def _loan_action(name):
    def handler(self, request, pk=None):
        return self.perform_action(request, pk, name)
    handler.__name__ = 'return_device' if name == 'return' else name
    return action(detail=True, methods=['post'], url_path=name)(handler)


for _name in ['submit', 'approve', 'reject', 'withdraw', 'issue', 'undo_issue', 'receive', 'return', 'inspect']:
    setattr(LoanViewSet, 'return_device' if _name == 'return' else _name, _loan_action(_name))


class DashboardView(APIView):
    def get(self, request):
        loans = scoped_requests(request.user)
        today = timezone.localdate()
        code = role(request.user)
        if code == 'manager':
            pending = loans.filter(status='pending').count()
        elif code == 'custodian':
            pending = loans.filter(status__in=['approved', 'return_pending']).count()
        elif code == 'employee':
            pending = loans.filter(status='handover').count()
        else:
            pending = loans.filter(status='pending').count()
        durations = [(x.decided_at - x.submitted_at).total_seconds() / 3600 for x in loans.filter(decided_at__isnull=False, submitted_at__isnull=False)]
        metrics = {'pending': pending, 'active': loans.filter(status__in=['borrowed', 'return_pending']).count(),
                   'overdue': loans.filter(status__in=['borrowed', 'return_pending'], due_date__lt=today).count(),
                   'available': Asset.objects.filter(status='available').count(), 'inspection': loans.filter(status='return_pending').count(),
                   'avg_approval_hours': round(sum(durations)/len(durations), 2) if durations else 0,
                   'total': loans.count()}
        by_status = [{'name': dict(LoanRequest.STATUS)[x['status']], 'status': x['status'], 'value': x['value']} for x in loans.values('status').annotate(value=Count('id')).order_by('status')]
        trend = []
        for offset in range(6, -1, -1):
            date = today - timedelta(days=offset)
            trend.append({'date': str(date), 'count': loans.filter(created_at__date=date).count()})
        return Response({'metrics': metrics, 'by_status': by_status, 'recent': LoanSerializer(loans[:6], many=True, context={'request': request}).data, 'trend': trend})


class AuditViewSet(viewsets.GenericViewSet):
    serializer_class = EventSerializer

    def list(self, request):
        require_role(request.user, 'admin', 'custodian')
        qs = LoanEvent.objects.select_related('actor__loan_profile', 'request', 'asset').order_by('-created_at', '-id')
        page = self.paginate_queryset(qs)
        return self.get_paginated_response(self.get_serializer(page, many=True).data)


class AccountViewSet(ObjectBodyMixin, viewsets.GenericViewSet):
    queryset = User.objects.none()
    def list(self, request):
        require_role(request.user, 'admin')
        qs = User.objects.select_related('role', 'loan_profile__store').order_by('id')
        q = request.query_params.get('q', '')
        if q:
            qs = qs.filter(Q(username__icontains=q) | Q(loan_profile__display_name__icontains=q))
        page = self.paginate_queryset(qs)
        return self.get_paginated_response([user_data(x) for x in page])

    def create(self, request):
        require_role(request.user, 'admin')
        return self.save_account(request)

    def partial_update(self, request, pk=None):
        require_role(request.user, 'admin')
        return self.save_account(request, get_object_or_404(User, pk=pk))

    @staticmethod
    def save_account(request, user=None):
        data = request.data
        allowed = {'username', 'email', 'password', 'display_name', 'role', 'store_id', 'status'}
        if set(data) - allowed:
            raise ValidationError('包含不允许修改的账号字段。')
        creating = user is None
        if creating:
            username = str(data.get('username', '')).strip()
            if not username or len(username) > 50:
                raise ValidationError({'username': '请输入1至50字的账号。'})
            user = User(username=username)
        elif 'username' in data and data['username'] != user.username:
            raise ValidationError({'username': '账号创建后不可修改。'})
        item = profile(user) if user.pk else None
        code = data.get('role', role(user))
        if not isinstance(code, str) or code not in {'employee', 'manager', 'custodian', 'admin'}:
            raise ValidationError({'role': '请选择有效角色。'})
        enabled = data.get('status', user.status)
        if enabled not in [0, 1] or isinstance(enabled, str):
            raise ValidationError({'status': '状态应为0或1。'})
        if user.pk == request.user.pk and (enabled == 0 or code != 'admin'):
            raise ValidationError('不能停用自己或移除自己的管理员身份。')
        store_id = data.get('store_id', item.store_id if item else None)
        store = None
        if code in {'employee', 'manager'}:
            if store_id is not None:
                store_id = serializers.IntegerField(min_value=1, max_value=9223372036854775807).run_validation(store_id)
            store = get_object_or_404(Store, pk=store_id) if store_id else None
            if not store:
                raise ValidationError({'store_id': '员工和店长必须关联门店。'})
        if user.pk and (code != role(user) or enabled == 0 or (item and item.store_id != (store.id if store else None))):
            busy = LoanRequest.objects.filter(applicant=user).exclude(status__in=['returned', 'rejected', 'withdrawn', 'draft']).exists()
            pending = Store.objects.filter(manager=user, loanrequest__status='pending').exists()
            if busy or pending:
                raise Conflict('该账号仍有在办申请或审批待办，请处理后再变更。')
            if user.managed_stores.exists() and (code != 'manager' or enabled == 0 or not store or user.managed_stores.exclude(pk=store.id).exists()):
                raise Conflict('请先在门店设置中解除该账号的店长关联。')
        email = str(data.get('email', user.email or user.username + '@demo.storeflow.local')).strip()
        from django.core.validators import validate_email
        try:
            validate_email(email)
        except DjangoValidationError:
            raise ValidationError({'email': '邮箱格式不正确。'})
        password = data.get('password')
        if password is not None and not isinstance(password, str):
            raise ValidationError({'password': '密码必须为文本。'})
        if creating and not password:
            raise ValidationError({'password': '创建账号必须设置密码。'})
        if password:
            try:
                validate_password(password, user)
            except DjangoValidationError as exc:
                raise ValidationError({'password': exc.messages})
            user.set_password(password)
        display_name = str(data.get('display_name', item.display_name if item else user.username)).strip()
        if not 1 <= len(display_name) <= 80:
            raise ValidationError({'display_name': '名称长度应为1至80字。'})
        with transaction.atomic():
            user.role, _ = Role.objects.get_or_create(code=code, defaults={'name': code})
            user.email, user.status, user.is_active = email, enabled, bool(enabled)
            try:
                user.save()
            except IntegrityError:
                raise ValidationError('账号或邮箱已存在。')
            LoanProfile.objects.update_or_create(user=user, defaults={'store': store, 'display_name': display_name})
            user._state.fields_cache.pop('loan_profile', None)
            event(None, request.user, 'account_create' if creating else 'account_update', '', '', user.username)
        return Response(user_data(user), status=201 if creating else 200)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except Exception:
        return Response({'status': 'not_ready', 'version': '1.0.0', 'database': 'unavailable', 'demo_mode': settings.DEMO_MODE}, status=503)
    return Response({'status': 'ok', 'version': '1.0.0', 'database': connection.vendor, 'demo_mode': settings.DEMO_MODE})


def frontend(request, path=''):
    if path.startswith('api/') or path == 'api':
        return JsonResponse({'detail': '接口不存在。'}, status=404)
    root = settings.FRONTEND_DIST_DIR
    candidate = (root / path).resolve()
    if not candidate.is_relative_to(root):
        return JsonResponse({'detail': '路径无效。'}, status=404)
    if candidate.is_file():
        response = FileResponse(candidate.open('rb'), content_type=mimetypes.guess_type(candidate.name)[0] or 'application/octet-stream')
        response['Cache-Control'] = 'public, max-age=86400' if path.startswith('assets/') else 'no-cache'
        return response
    if path.startswith('assets/'):
        return JsonResponse({'detail': '静态文件不存在。'}, status=404)
    index = root / 'index.html'
    if not index.exists():
        return HttpResponse('前端尚未构建。请进入 frontend 目录执行 npm ci 和 npm run build，或恢复发行版自带的 frontend/dist。', status=503, content_type='text/plain; charset=utf-8')
    response = FileResponse(index.open('rb'), content_type='text/html; charset=utf-8')
    response['Cache-Control'] = 'no-cache'
    return response


from .schema import document_api
document_api(globals())
