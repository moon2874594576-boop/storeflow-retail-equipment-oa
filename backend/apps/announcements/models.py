from django.db import models

class Announcement(models.Model):
    PRIORITY_CHOICES = (
        (1, '普通'),
        (2, '重要'),
        (3, '紧急'),
    )
    STATUS_CHOICES = (
        (0, '草稿'),
        (1, '已发布'),
        (2, '已撤回'),
    )

    title = models.CharField('公告标题', max_length=200)
    content = models.TextField('公告内容')
    publisher = models.ForeignKey('users.User', on_delete=models.CASCADE, 
                                  related_name='published_announcements', verbose_name='发布人')
    department = models.ForeignKey('employees.Department', on_delete=models.SET_NULL, 
                                    null=True, blank=True, verbose_name='发布部门')
    priority = models.SmallIntegerField('优先级', choices=PRIORITY_CHOICES, default=1)
    status = models.SmallIntegerField('状态', choices=STATUS_CHOICES, default=0)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'announcements_announcement'
        verbose_name = '公告'
        verbose_name_plural = '公告管理'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def priority_display(self):
        return self.get_priority_display()

    @property
    def status_display(self):
        return self.get_status_display()

class AnnouncementRead(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, 
                                     related_name='reads', verbose_name='公告')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    read_at = models.DateTimeField('阅读时间', auto_now_add=True)

    class Meta:
        db_table = 'announcements_announcement_read'
        verbose_name = '公告已读记录'
        verbose_name_plural = '公告已读记录'
        unique_together = ['announcement', 'user']

    def __str__(self):
        return f'{self.user} - {self.announcement}'
