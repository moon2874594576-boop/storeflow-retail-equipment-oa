from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from . import test_workflow as workflow_tests
from apps.loans.models import LoanRequest, LoanEvent, Asset
from apps.users.models import User


class IntegrityTests(TestCase):
    setUp = workflow_tests.WorkflowTests.setUp
    login = workflow_tests.WorkflowTests.login
    create = workflow_tests.WorkflowTests.create
    action = workflow_tests.WorkflowTests.action
    issue = workflow_tests.WorkflowTests.issue

    def test_invalid_json_shapes_are_validation_errors(self):
        self.login('admin')
        self.assertEqual(self.client.post('/api/accounts/', ['unexpected'], format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/accounts/', {'username': 'malformed', 'role': ['admin'], 'password': 'Safe-Test-2026!'}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/auth/change_password/', {'old_password': 'Test-Password2026!', 'new_password': ['invalid']}, format='json').status_code, 400)

    def test_moved_employee_draft_cannot_submit_to_previous_store(self):
        pk = self.create()
        self.login('admin')
        response = self.client.patch(f'/api/accounts/{self.users["employee"].id}/', {'store_id': self.other.id}, format='json')
        self.assertEqual(response.status_code, 200)
        self.action('employee', pk, 'submit', expected=400)
        self.assertEqual(LoanRequest.objects.get(pk=pk).status, 'draft')
        self.action('employee', pk, 'withdraw')

    def test_password_change_revokes_existing_access_and_refresh(self):
        response = self.client.post('/api/auth/login/', {'username': 'employee', 'password': 'Test-Password2026!'}, format='json')
        access, refresh = response.data['access'], response.data['refresh']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        response = self.client.post('/api/auth/change_password/', {'old_password': 'Test-Password2026!', 'new_password': 'New-Safe-2026!'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)
        self.client.credentials()
        self.assertEqual(self.client.post('/api/auth/refresh/', {'refresh': refresh}).status_code, 401)

    def test_account_response_and_database_profile_match(self):
        self.login('admin')
        response = self.client.patch(f'/api/accounts/{self.users["employee"].id}/', {'display_name': '更新后的名字'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['display_name'], '更新后的名字')
        response = self.client.post('/api/accounts/', {'username': 'newemployee', 'password': 'Safe-Test-2026!', 'display_name': '新员工', 'role': 'employee', 'store_id': self.store.id}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['store_id'], self.store.id)
        self.assertEqual(response.data['display_name'], '新员工')

    def test_account_duplicate_and_self_disable_are_safe(self):
        self.login('admin')
        response = self.client.post('/api/accounts/', {'username': 'employee', 'password': 'Safe-Test-2026!', 'role': 'employee', 'store_id': self.store.id}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.filter(username='employee').count(), 1)
        self.assertEqual(self.client.patch(f'/api/accounts/{self.users["admin"].id}/', {'status': 0}, format='json').status_code, 400)

    def test_busy_account_cannot_be_disabled_or_moved(self):
        pk = self.create()
        self.action('employee', pk, 'submit')
        self.login('admin')
        self.assertEqual(self.client.patch(f'/api/accounts/{self.users["employee"].id}/', {'status': 0}, format='json').status_code, 409)
        self.assertEqual(self.client.patch(f'/api/accounts/{self.users["employee"].id}/', {'store_id': self.other.id}, format='json').status_code, 409)

    def test_profile_cannot_change_privilege(self):
        self.login('employee')
        self.assertEqual(self.client.patch('/api/auth/me/', {'role': 'admin'}, format='json').status_code, 400)
        self.users['employee'].refresh_from_db()
        self.assertEqual(self.users['employee'].role.code, 'employee')

    def test_past_date_or_empty_purpose_rejected(self):
        self.login('employee')
        for payload in [
            {'category_id': self.category.id, 'purpose': 'valid', 'due_date': str(timezone.localdate()-timedelta(days=1))},
            {'category_id': self.category.id, 'purpose': ' ', 'due_date': str(timezone.localdate())},
            {'category_id': self.category.id, 'purpose': 'valid', 'due_date': str(timezone.localdate()), 'applicant_id': self.users['admin'].id},
        ]:
            self.assertEqual(self.client.post('/api/requests/', payload).status_code, 400)

    def test_invalid_inspection_rolls_back_all_changes(self):
        pk = self.create()
        self.issue(pk)
        self.action('employee', pk, 'receive')
        self.action('employee', pk, 'return')
        count = LoanEvent.objects.count()
        self.action('custodian', pk, 'inspect', {'condition': 'damaged'}, expected=400)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, 'inspection')
        self.assertEqual(LoanRequest.objects.get(pk=pk).status, 'return_pending')
        self.assertEqual(LoanEvent.objects.count(), count)

    def test_occupied_asset_cannot_be_edited_or_force_freed(self):
        pk = self.create()
        self.issue(pk)
        self.login('custodian')
        self.assertEqual(self.client.patch(f'/api/assets/{self.asset.id}/', {'name': 'changed'}, format='json').status_code, 409)
        self.assertEqual(self.client.post(f'/api/assets/{self.asset.id}/repair/', {'reason': 'bypass'}).status_code, 409)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, 'handover')

    def test_asset_status_cannot_be_set_directly(self):
        self.login('custodian')
        self.assertEqual(self.client.patch(f'/api/assets/{self.asset.id}/', {'status': 'in_use'}, format='json').status_code, 400)

    def test_export_escapes_spreadsheet_formulas(self):
        pk = self.create()
        self.login('employee')
        self.client.patch(f'/api/requests/{pk}/', {'purpose': '=SUM(1,2)'}, format='json')
        text = self.client.get('/api/requests/export/').content.decode('utf-8-sig')
        self.assertIn("'=SUM(1,2)", text)

    def test_other_store_manager_cannot_approve(self):
        pk = self.create()
        self.action('employee', pk, 'submit')
        user = self.users['manager']
        user.loan_profile.store = self.other
        user.loan_profile.save()
        self.login('manager')
        self.assertEqual(self.client.post(f'/api/requests/{pk}/approve/', {}).status_code, 404)

    def test_invalid_query_does_not_crash(self):
        self.login('employee')
        for endpoint in ['/api/requests/?store_id=abc', '/api/assets/?category_id=abc']:
            self.assertEqual(self.client.get(endpoint).status_code, 400)

    def test_audit_permissions_and_no_deletion(self):
        pk = self.create()
        self.login('employee')
        self.assertEqual(self.client.get('/api/audit/').status_code, 403)
        self.assertEqual(self.client.delete(f'/api/requests/{pk}/').status_code, 405)
        self.login('admin')
        self.assertGreaterEqual(self.client.get('/api/audit/').data['count'], 1)

    def test_no_staff_api_allows_staff_impersonation(self):
        self.login('employee')
        self.assertEqual(self.client.post('/api/accounts/', {'role': 'admin'}).status_code, 403)
        self.assertEqual(self.client.patch(f'/api/accounts/{self.users["employee"].id}/', {'role': 'admin'}, format='json').status_code, 403)

    def test_empty_health_is_anonymous_and_no_paths_or_credentials(self):
        self.client.force_authenticate(None)
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {'status', 'version', 'database', 'demo_mode'})
