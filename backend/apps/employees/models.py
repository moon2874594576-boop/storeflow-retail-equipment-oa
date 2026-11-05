from django.db import models

class Department(models.Model):
    name = models.CharField('部门名称', max_length=100)
    code = models.CharField('部门编码', max_length=50, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                               verbose_name='上级部门', related_name='children')
    manager = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='部门负责人')
    sort = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'employees_department'
        verbose_name = '部门'
        verbose_name_plural = '部门管理'
        ordering = ['sort']

    def __str__(self):
        return self.name

    @property
    def children_list(self):
        return self.children.all()

class Position(models.Model):
    name = models.CharField('岗位名称', max_length=50)
    code = models.CharField('岗位编码', max_length=50, unique=True)
    description = models.TextField('岗位描述', blank=True)

    class Meta:
        db_table = 'employees_position'
        verbose_name = '岗位'
        verbose_name_plural = '岗位管理'

    def __str__(self):
        return self.name

class Employee(models.Model):
    GENDER_CHOICES = (
        (0, '女'),
        (1, '男'),
    )
    STATUS_CHOICES = (
        (0, '离职'),
        (1, '在职'),
    )

    employee_no = models.CharField('工号', max_length=20, unique=True)
    name = models.CharField('姓名', max_length=50)
    gender = models.SmallIntegerField('性别', choices=GENDER_CHOICES, default=1)
    id_card = models.CharField('身份证号', max_length=18, blank=True)
    phone = models.CharField('手机号', max_length=20, blank=True)
    email = models.EmailField('邮箱', max_length=100, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='所属部门')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name='岗位')
    entry_date = models.DateField('入职日期', null=True, blank=True)
    status = models.SmallIntegerField('状态', choices=STATUS_CHOICES, default=1)
    user = models.OneToOneField('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='关联账号')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'employees_employee'
        verbose_name = '员工'
        verbose_name_plural = '员工管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.employee_no} - {self.name}'

    @property
    def gender_display(self):
        return self.get_gender_display()

    @property
    def status_display(self):
        return self.get_status_display()
