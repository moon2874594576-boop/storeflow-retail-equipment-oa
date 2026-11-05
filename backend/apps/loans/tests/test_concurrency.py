"""Run against real PostgreSQL in CI; local SQLite HTTP concurrency is checked separately."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless
from django.db import connection, connections
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from apps.users.models import User
from apps.loans.models import Asset, LoanRequest, LoanEvent
from . import test_workflow as workflow_tests


@skipUnless(connection.vendor == 'postgresql', 'PostgreSQL independent-connection concurrency test; enabled by CI DATABASE_URL')
class PostgreSQLConcurrencyTests(TransactionTestCase):
    setUp = workflow_tests.WorkflowTests.setUp
    login = workflow_tests.WorkflowTests.login
    create = workflow_tests.WorkflowTests.create
    action = workflow_tests.WorkflowTests.action

    def race(self, role, jobs):
        gate = Barrier(2)
        actor_id = self.users[role].id

        def worker(job):
            try:
                client = APIClient()
                client.force_authenticate(User.objects.get(pk=actor_id))
                gate.wait(timeout=10)
                pk, action_name, payload = job
                response = client.post(f'/api/requests/{pk}/{action_name}/', payload, format='json')
                return response.status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(worker, jobs))
        self.assertEqual(sorted(results), [200, 409])

    def test_two_requests_compete_for_same_asset(self):
        ids = [self.create(), self.create()]
        for pk in ids:
            self.action('employee', pk, 'submit')
            self.action('manager', pk, 'approve')
        self.race('custodian', [(pk, 'issue', {'asset_id': self.asset.id}) for pk in ids])
        self.assertEqual(LoanRequest.objects.filter(asset=self.asset, status='handover').count(), 1)
        self.assertEqual(LoanRequest.objects.filter(pk__in=ids, status='approved').count(), 1)
        self.assertEqual(LoanEvent.objects.filter(request_id__in=ids, action='issue').count(), 1)
        self.assertEqual(Asset.objects.get(pk=self.asset.pk).status, 'handover')

    def test_same_pending_approval_only_one_decision(self):
        pk = self.create()
        self.action('employee', pk, 'submit')
        self.race('manager', [(pk, 'approve', {}), (pk, 'approve', {})])
        self.assertEqual(LoanEvent.objects.filter(request_id=pk, action='approve').count(), 1)
        self.assertEqual(LoanRequest.objects.get(pk=pk).status, 'approved')
