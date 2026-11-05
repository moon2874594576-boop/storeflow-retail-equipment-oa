from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from apps.users.models import User, Role
from apps.loans.models import Store, LoanProfile, Category, Asset, LoanRequest, LoanEvent


class WorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.store = Store.objects.create(code='A', name='测试店A')
        self.other = Store.objects.create(code='B', name='测试店B')
        self.users = {}
        for code, store in [('employee', self.store), ('manager', self.store), ('custodian', None), ('admin', None), ('outsider', self.other)]:
            role_code = 'employee' if code == 'outsider' else code
            role, _ = Role.objects.get_or_create(code=role_code, defaults={'name': role_code})
            user = User.objects.create_user(username=code, email=f'{code}@example.test', password='Test-Password2026!', role=role)
            LoanProfile.objects.create(user=user, store=store, display_name=code)
            self.users[code] = user
        self.store.manager = self.users['manager']
        self.store.save()
        self.category = Category.objects.create(name='扫码枪', code='scanner')
        self.asset = Asset.objects.create(code='SC-001', name='测试扫码枪', serial_number='SER-001', category=self.category)

    def login(self, role):
        self.client.force_authenticate(self.users[role])

    def create(self):
        self.login('employee')
        response = self.client.post('/api/requests/', {'category_id': self.category.id, 'purpose': '门店盘点', 'due_date': str(timezone.localdate() + timedelta(days=7))})
        self.assertEqual(response.status_code, 201, response.data)
        return response.data['id']

    def action(self, role, pk, action, payload=None, expected=200):
        self.login(role)
        response = self.client.post(f'/api/requests/{pk}/{action}/', payload or {}, format='json')
        self.assertEqual(response.status_code, expected, getattr(response, 'data', ''))
        return response

    def issue(self, pk):
        self.action('employee', pk, 'submit')
        self.action('manager', pk, 'approve')
        self.action('custodian', pk, 'issue', {'asset_id': self.asset.id})

    def test_complete_normal_flow(self):
        pk = self.create()
        self.issue(pk)
        self.action('employee', pk, 'receive')
        self.action('employee', pk, 'return')
        result = self.action('custodian', pk, 'inspect', {'condition': 'normal'})
        self.assertEqual(result.data['status'], 'returned')
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, 'available')
        self.assertEqual(LoanEvent.objects.filter(request_id=pk).count(), 7)

    def test_damaged_return_requires_repair(self):
        pk = self.create()
        self.issue(pk)
        self.action('employee', pk, 'receive')
        self.action('employee', pk, 'return')
        self.action('custodian', pk, 'inspect', {'condition': 'damaged', 'reason': '按键损坏'})
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, 'maintenance')
        self.login('custodian')
        response = self.client.post(f'/api/assets/{self.asset.id}/repair/', {'reason': '更换按键并测试完成'})
        self.assertEqual(response.status_code, 200)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, 'available')

    def test_undo_issue_releases_device_and_preserves_audit(self):
        pk = self.create()
        self.issue(pk)
        self.action('custodian', pk, 'undo_issue', {'reason': '交接时发现型号错误'})
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, 'available')
        self.assertEqual(LoanRequest.objects.get(pk=pk).status, 'approved')
        self.assertTrue(LoanEvent.objects.filter(request_id=pk, action='undo_issue').exists())

    def test_cross_store_detail_and_export_are_scoped(self):
        pk = self.create()
        self.action('employee', pk, 'submit')
        self.login('outsider')
        self.assertEqual(self.client.get(f'/api/requests/{pk}/').status_code, 404)
        self.assertEqual(self.client.get('/api/requests/').data['count'], 0)
        self.assertNotIn('门店盘点', self.client.get('/api/requests/export/').content.decode('utf-8-sig'))

    def test_roles_cannot_change_status_with_patch(self):
        pk = self.create()
        self.login('employee')
        self.assertEqual(self.client.patch(f'/api/requests/{pk}/', {'status': 'returned'}, format='json').status_code, 400)
        self.action('employee', pk, 'approve', expected=403)
        self.login('employee')
        self.assertEqual(self.client.get('/api/accounts/').status_code, 403)
        self.assertEqual(self.client.post('/api/assets/', {}).status_code, 403)

    def test_duplicate_action_conflicts_without_extra_event(self):
        pk = self.create()
        self.action('employee', pk, 'submit')
        self.action('manager', pk, 'approve')
        count = LoanEvent.objects.count()
        self.action('manager', pk, 'approve', expected=409)
        self.assertEqual(LoanEvent.objects.count(), count)

    def test_two_requests_cannot_share_one_device(self):
        first = self.create()
        self.issue(first)
        second = self.create()
        self.action('employee', second, 'submit')
        self.action('manager', second, 'approve')
        self.action('custodian', second, 'issue', {'asset_id': self.asset.id}, expected=409)
        self.assertEqual(LoanRequest.objects.get(pk=second).status, 'approved')

    def test_expired_issue_is_rejected(self):
        pk = self.create()
        self.action('employee', pk, 'submit')
        self.action('manager', pk, 'approve')
        LoanRequest.objects.filter(pk=pk).update(due_date=timezone.localdate() - timedelta(days=1))
        self.action('custodian', pk, 'issue', {'asset_id': self.asset.id}, expected=400)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, 'available')

    def test_withdraw_before_issue_and_reject_reason(self):
        pk = self.create()
        self.action('employee', pk, 'submit')
        self.action('manager', pk, 'reject', expected=400)
        self.action('manager', pk, 'reject', {'reason': '用途需要进一步说明'})
        pk = self.create()
        self.action('employee', pk, 'submit')
        self.action('employee', pk, 'withdraw')
        self.action('manager', pk, 'approve', expected=409)

    def test_unauthenticated_and_legacy_routes_closed(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/requests/').status_code, 401)
        for route in ['approvals', 'users', 'employees', 'announcements']:
            self.assertEqual(self.client.get(f'/api/{route}/').status_code, 404)

    def test_disabled_account_existing_token_is_rejected(self):
        response = self.client.post('/api/auth/login/', {'username': 'employee', 'password': 'Test-Password2026!'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.users['employee'].status = 0
        self.users['employee'].save()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)

    def test_dashboard_counts_are_role_scoped(self):
        pk = self.create()
        self.action('employee', pk, 'submit')
        self.login('manager')
        self.assertEqual(self.client.get('/api/dashboard/').data['metrics']['pending'], 1)
        self.login('outsider')
        self.assertEqual(self.client.get('/api/dashboard/').data['metrics']['pending'], 0)

    def test_draft_patch_is_limited_and_draft_private(self):
        pk = self.create()
        self.login('employee')
        self.assertEqual(self.client.patch(f'/api/requests/{pk}/', {'purpose': '更新用途'}, format='json').status_code, 200)
        self.login('manager')
        self.assertEqual(self.client.get(f'/api/requests/{pk}/').status_code, 404)

    def test_category_mismatch_cannot_be_issued(self):
        pk = self.create()
        self.action('employee', pk, 'submit')
        self.action('manager', pk, 'approve')
        category = Category.objects.create(name='平板', code='tablet')
        bad = Asset.objects.create(code='TAB-1', name='平板', serial_number='TAB-S1', category=category)
        self.action('custodian', pk, 'issue', {'asset_id': bad.id}, expected=400)
