from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from rest_framework import serializers
from .models import Asset, LoanRequest, LoanEvent, LoanProfile

ACTION_LABELS = {'create': '创建草稿', 'submit': '提交申请', 'approve': '店长通过', 'reject': '店长驳回',
                 'withdraw': '撤回申请', 'issue': '发放设备', 'undo_issue': '撤销发放', 'receive': '确认签收',
                 'return': '申请归还', 'inspect': '归还验收', 'repair': '确认修复', 'edit': '更新草稿',
                 'account_update': '更新账号', 'account_create': '创建账号', 'asset_update': '更新台账', 'asset_create': '新增设备', 'store_update': '更新门店'}


class Conflict(APIException):
    status_code = 409
    default_detail = '记录状态已变化，请刷新后重试。'


def role(user):
    return user.role.code if user.role_id else ''


def profile(user):
    return getattr(user, 'loan_profile', None)


def user_name(user):
    item = profile(user)
    return (item.display_name if item else '') or user.username


def scoped_requests(user):
    qs = LoanRequest.objects.select_related('applicant__loan_profile', 'store', 'category', 'asset')
    code = role(user)
    if code == 'employee':
        return qs.filter(applicant=user)
    if code == 'manager':
        item = profile(user)
        return qs.filter(store_id=item.store_id).exclude(status='draft') if item and item.store_id else qs.none()
    if code in {'admin', 'custodian'}:
        return qs.exclude(status='draft')
    return qs.none()


def actor_can(user, loan, action):
    code = role(user)
    if action in {'submit', 'withdraw', 'receive', 'return', 'edit'}:
        return code == 'employee' and loan.applicant_id == user.id
    if action in {'approve', 'reject'}:
        item = profile(user)
        return code == 'manager' and item and item.store_id == loan.store_id and loan.store.manager_id == user.id and loan.applicant_id != user.id
    return code == 'custodian' and action in {'issue', 'undo_issue', 'inspect'}


ALLOWED = {'submit': {'draft'}, 'withdraw': {'draft', 'pending', 'approved'}, 'approve': {'pending'},
           'reject': {'pending'}, 'issue': {'approved'}, 'undo_issue': {'handover'},
           'receive': {'handover'}, 'return': {'borrowed'}, 'inspect': {'return_pending'}, 'edit': {'draft'}}


def available_actions(user, loan):
    return [action for action, states in ALLOWED.items() if loan.status in states and actor_can(user, loan, action)]


def validate_due(due_date):
    if due_date < timezone.localdate():
        raise ValidationError({'due_date': '预计归还日期不能早于今天；过期申请请撤回后重新提交。'})


def event(loan, user, action, old, new, reason='', asset=None):
    return LoanEvent.objects.create(request=loan, asset=asset or (loan.asset if loan else None), actor=user,
                                    action=action, from_status=old, to_status=new, reason=reason)


def transition(user, loan, action, data):
    if not actor_can(user, loan, action):
        raise PermissionDenied('当前角色不能执行此操作。')
    if action not in ALLOWED or loan.status not in ALLOWED[action]:
        raise Conflict()
    reason = str(data.get('reason', '')).strip()
    if len(reason) > 1000:
        raise ValidationError({'reason': '说明不能超过1000字。'})
    if action in {'reject', 'undo_issue'} and not reason:
        raise ValidationError({'reason': '请填写操作原因。'})
    with transaction.atomic():
        # SQLite 先执行条件写操作以获得写锁；PostgreSQL 同时锁定申请行。
        if not LoanRequest.objects.filter(pk=loan.pk, status=loan.status).update(updated_at=timezone.now()):
            raise Conflict()
        current = LoanRequest.objects.select_for_update().get(pk=loan.pk)
        old = current.status
        touched_asset = current.asset
        if action == 'submit':
            current_store_id = LoanProfile.objects.filter(user_id=user.id).values_list('store_id', flat=True).first()
            if current_store_id != current.store_id:
                raise ValidationError('所属门店已变化，请撤回旧草稿后重新申请。')
            validate_due(current.due_date)
            manager = current.store.manager
            if not manager or not manager.is_active or manager.status != 1 or role(manager) != 'manager':
                raise ValidationError('该门店尚未配置可用店长，请联系管理员。')
            current.status = 'pending'
            current.submitted_at = timezone.now()
        elif action == 'approve':
            current.status, current.decided_at = 'approved', timezone.now()
        elif action == 'reject':
            current.status, current.decided_at = 'rejected', timezone.now()
        elif action == 'withdraw':
            current.status = 'withdrawn'
        elif action == 'issue':
            validate_due(current.due_date)
            asset_id = serializers.IntegerField(min_value=1, max_value=9223372036854775807).run_validation(data.get('asset_id'))
            try:
                asset = Asset.objects.select_for_update().get(pk=asset_id)
            except (Asset.DoesNotExist, ValueError, TypeError):
                raise ValidationError({'asset_id': '请选择有效设备。'})
            if asset.category_id != current.category_id:
                raise ValidationError({'asset_id': '设备类别与申请不一致。'})
            if not Asset.objects.filter(pk=asset.pk, status='available').update(status='handover', updated_at=timezone.now()):
                raise Conflict('该设备已被占用，请重新选择。')
            current.asset, touched_asset, current.status = asset, asset, 'handover'
        elif action == 'undo_issue':
            if not Asset.objects.filter(pk=current.asset_id, status='handover').update(status='available', updated_at=timezone.now()):
                raise Conflict('设备状态与交接记录不一致，请联系管理员。')
            current.asset, current.status = None, 'approved'
        elif action == 'receive':
            if not Asset.objects.filter(pk=current.asset_id, status='handover').update(status='in_use', updated_at=timezone.now()):
                raise Conflict('设备状态已变化。')
            current.status = 'borrowed'
        elif action == 'return':
            if not Asset.objects.filter(pk=current.asset_id, status='in_use').update(status='inspection', updated_at=timezone.now()):
                raise Conflict('设备状态已变化。')
            current.status = 'return_pending'
        elif action == 'inspect':
            condition = data.get('condition')
            if not isinstance(condition, str) or condition not in {'normal', 'damaged'}:
                raise ValidationError({'condition': '请选择 normal 或 damaged。'})
            if condition == 'damaged' and not reason:
                raise ValidationError({'reason': '异常验收必须填写设备问题。'})
            target = 'available' if condition == 'normal' else 'maintenance'
            if not Asset.objects.filter(pk=current.asset_id, status='inspection').update(status=target, updated_at=timezone.now()):
                raise Conflict('设备状态已变化。')
            current.status, current.returned_at = 'returned', timezone.now()
            reason = ('验收正常' if condition == 'normal' else '验收异常，转待维修') + ('：' + reason if reason else '')
        current.save()
        event(current, user, action, old, current.status, reason, touched_asset)
        return current
