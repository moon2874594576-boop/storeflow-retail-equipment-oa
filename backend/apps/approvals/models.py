from django.db import models

class ApprovalType(models.Model):
    name = models.CharField('审批名称', max_length=50)
    code = models.CharField('审批编码', max_length=50, unique=True)
    description = models.TextField('审批描述', blank=True)
    fields = models.JSONField('表单字段配置', default=list)
    approvers = models.JSONField('审批人配置', default=list)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'approvals_approval_type'
        verbose_name = '审批类型'
        verbose_name_plural = '审批类型管理'

    def __str__(self):
        return self.name

class Approval(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审批'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
        ('revoked', '已撤回'),
    )

    type = models.ForeignKey(ApprovalType, on_delete=models.CASCADE, verbose_name='审批类型')
    title = models.CharField('审批标题', max_length=200)
    content = models.JSONField('审批内容', default=dict)
    applicant = models.ForeignKey('users.User', on_delete=models.CASCADE, 
                                  related_name='approvals_applied', verbose_name='申请人')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    current_approver = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True,
                                          blank=True, verbose_name='当前审批人')
    created_at = models.DateTimeField('申请时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'approvals_approval'
        verbose_name = '审批单'
        verbose_name_plural = '审批单管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.get_status_display()}'

    @property
    def status_display(self):
        return self.get_status_display()

class ApprovalRecord(models.Model):
    ACTION_CHOICES = (
        ('approve', '通过'),
        ('reject', '驳回'),
        ('cc', '抄送'),
    )

    approval = models.ForeignKey(Approval, on_delete=models.CASCADE, 
                                 related_name='records', verbose_name='审批单')
    approver = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='审批人')
    action = models.CharField('操作', max_length=20, choices=ACTION_CHOICES)
    comment = models.TextField('审批意见', blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        db_table = 'approvals_approval_record'
        verbose_name = '审批记录'
        verbose_name_plural = '审批记录管理'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.approver} - {self.get_action_display()}'
