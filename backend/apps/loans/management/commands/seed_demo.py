import os
from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from apps.users.models import User, Role
from apps.loans.models import Store, LoanProfile, Category, Asset, LoanRequest, LoanEvent
from apps.loans.services import transition


class Command(BaseCommand):
    help = 'Create fictional demonstration data once; never resets existing passwords or business records.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEMO_MODE:
            raise CommandError('演示模式未启用，拒绝创建演示账号。设置 STOREFLOW_DEMO=1 后重试。')
        password = os.environ.get('STOREFLOW_DEMO_PASSWORD', 'Demo2026!')
        if len(password) < 8:
            raise CommandError('演示密码至少需要8位。')
        roles = {}
        for code, name in [('employee', '门店员工'), ('manager', '店长'), ('custodian', '设备管理员'), ('admin', '系统管理员')]:
            roles[code], _ = Role.objects.get_or_create(code=code, defaults={'name': name})
        stores = [Store.objects.get_or_create(code=code, defaults={'name': name})[0] for code, name in [('FZ-01', '福州·榕城示范店'), ('FZ-02', '福州·江滨示范店')]]
        users = {}
        for username, display_name, code, store in [
            ('employee_a', '林小满', 'employee', stores[0]), ('employee_b', '陈亦安', 'employee', stores[0]),
            ('employee_c', '王知夏', 'employee', stores[1]), ('employee_d', '李星禾', 'employee', stores[1]),
            ('manager_a', '赵店长', 'manager', stores[0]), ('manager_b', '周店长', 'manager', stores[1]),
            ('custodian', '许设备', 'custodian', None), ('admin', '系统管理员', 'admin', None),
        ]:
            user, created = User.objects.get_or_create(username=username, defaults={'email': username + '@demo.storeflow.local', 'role': roles[code]})
            if created:
                user.set_password(password)
                user.save()
            LoanProfile.objects.get_or_create(user=user, defaults={'display_name': display_name, 'store': store})
            users[username] = user
        for store, manager in zip(stores, [users['manager_a'], users['manager_b']]):
            if not store.manager_id:
                store.manager = manager
                store.save(update_fields=['manager'])
        categories = []
        for code, name in [('scanner', '扫码枪'), ('printer', '标签打印机'), ('tablet', '平板终端')]:
            categories.append(Category.objects.get_or_create(code=code, defaults={'name': name})[0])
        assets = []
        for i in range(20):
            category = categories[i % 3]
            asset, _ = Asset.objects.get_or_create(code=f'SF-DEV-{i+1:03}', defaults={'name': f'{category.name} · {i+1:02}', 'serial_number': f'DEMO-SN-{i+1:05}', 'category': category})
            assets.append(asset)
        # 初始化样例通过同一业务服务流转，不伪造脱离台账的状态；已存在的样例不重写。
        statuses = ['pending', 'approved', 'handover', 'borrowed', 'return_pending', 'returned', 'rejected', 'withdrawn', 'draft', 'borrowed', 'pending', 'approved']
        for i, target in enumerate(statuses):
            number = f'DEMO-2026-{i+1:03}'
            if LoanRequest.objects.filter(number=number).exists():
                continue
            asset = assets[i]
            if asset.status != 'available':
                continue
            employee = users['employee_a'] if i % 2 == 0 else users['employee_c']
            manager = users['manager_a'] if i % 2 == 0 else users['manager_b']
            loan = LoanRequest.objects.create(number=number, applicant=employee, store=employee.loan_profile.store, category=asset.category,
                purpose=['周末盘点与货架标签更新', '新员工培训临时设备', '促销期间收货扫码支援'][i % 3], due_date=timezone.localdate()+timedelta(days=7))
            LoanEvent.objects.create(request=loan, actor=employee, action='create', to_status='draft', reason='虚构演示数据')
            if target != 'draft':
                loan = transition(employee, loan, 'submit', {})
            if target == 'rejected':
                transition(manager, loan, 'reject', {'reason': '演示：门店现有设备可以满足需求'})
                continue
            if target == 'withdrawn':
                transition(employee, loan, 'withdraw', {'reason': '演示：培训计划调整'})
                continue
            if target in {'approved', 'handover', 'borrowed', 'return_pending', 'returned'}:
                loan = transition(manager, loan, 'approve', {})
            if target in {'handover', 'borrowed', 'return_pending', 'returned'}:
                loan = transition(users['custodian'], loan, 'issue', {'asset_id': asset.id})
            if target in {'borrowed', 'return_pending', 'returned'}:
                loan = transition(employee, loan, 'receive', {})
            if target in {'return_pending', 'returned'}:
                loan = transition(employee, loan, 'return', {})
            if target == 'returned':
                loan = transition(users['custodian'], loan, 'inspect', {'condition': 'normal', 'reason': '演示：设备外观及功能正常'})
            created_at = timezone.now() - timedelta(days=i % 7, hours=3)
            LoanRequest.objects.filter(pk=loan.pk).update(created_at=created_at)
            if i == 9:
                LoanRequest.objects.filter(pk=loan.pk).update(due_date=timezone.localdate()-timedelta(days=2))
        self.stdout.write(self.style.SUCCESS('StoreFlow 演示数据已就绪；已有账号密码和业务记录保持不变。'))
