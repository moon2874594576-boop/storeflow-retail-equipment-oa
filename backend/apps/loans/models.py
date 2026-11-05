import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Store(models.Model):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=80)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='managed_stores')

    def __str__(self):
        return self.name


class LoanProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loan_profile')
    store = models.ForeignKey(Store, on_delete=models.PROTECT, null=True, blank=True)
    display_name = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.display_name or self.user.username


class Category(models.Model):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class Asset(models.Model):
    STATUS = [('available', '空闲'), ('handover', '交接中'), ('in_use', '借用中'), ('inspection', '待验收'), ('maintenance', '待维修')]
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=80, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS, default='available', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.code} {self.name}'


def loan_number():
    return 'SF' + timezone.localdate().strftime('%Y%m%d') + uuid.uuid4().hex[:10].upper()


class LoanRequest(models.Model):
    STATUS = [('draft', '草稿'), ('pending', '待店长审批'), ('approved', '待发放'), ('handover', '待签收'),
              ('borrowed', '借用中'), ('return_pending', '待归还验收'), ('returned', '已归还'),
              ('rejected', '已驳回'), ('withdrawn', '已撤回')]
    number = models.CharField(max_length=40, unique=True, default=loan_number, editable=False)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='loan_requests')
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    purpose = models.CharField(max_length=1000)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS, default='draft', db_index=True)
    asset = models.ForeignKey(Asset, null=True, blank=True, on_delete=models.PROTECT, related_name='loan_requests')
    submitted_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
        constraints = [models.UniqueConstraint(fields=['asset'], condition=Q(status__in=['handover', 'borrowed', 'return_pending']), name='one_active_loan_per_asset')]

    @property
    def overdue(self) -> bool:
        return self.status in {'borrowed', 'return_pending'} and self.due_date < timezone.localdate()

    def __str__(self):
        return self.number


class LoanEvent(models.Model):
    request = models.ForeignKey(LoanRequest, on_delete=models.PROTECT, null=True, blank=True, related_name='events')
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, null=True, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=32)
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20, blank=True)
    reason = models.CharField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f'{self.action} @ {self.created_at}'
