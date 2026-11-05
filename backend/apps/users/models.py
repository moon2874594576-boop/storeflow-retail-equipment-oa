from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class Permission(models.Model):
    name = models.CharField('权限名称', max_length=100)
    code = models.CharField('权限编码', max_length=100, unique=True)
    module = models.CharField('所属模块', max_length=50)
    description = models.TextField('权限描述', blank=True)

    class Meta:
        db_table = 'users_permission'
        verbose_name = '权限'
        verbose_name_plural = '权限管理'

    def __str__(self):
        return f'{self.module} - {self.name}'

class Role(models.Model):
    name = models.CharField('角色名称', max_length=50, unique=True)
    code = models.CharField('角色编码', max_length=50, unique=True)
    description = models.TextField('角色描述', blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name='权限列表')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'users_role'
        verbose_name = '角色'
        verbose_name_plural = '角色管理'

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('用户名不能为空')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 1)
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = (
        (0, '禁用'),
        (1, '启用'),
    )

    username = models.CharField('用户名', max_length=50, unique=True)
    email = models.EmailField('邮箱', max_length=100, unique=True)
    phone = models.CharField('手机号', max_length=20, blank=True)
    avatar = models.CharField('头像', max_length=255, blank=True)
    status = models.SmallIntegerField('状态', choices=STATUS_CHOICES, default=1)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='角色')
    is_staff = models.BooleanField('是否管理员', default=False)
    is_active = models.BooleanField('是否激活', default=True)
    date_joined = models.DateTimeField('加入时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users_user'
        verbose_name = '用户'
        verbose_name_plural = '用户管理'

    def __str__(self):
        return self.username

    @property
    def role_name(self):
        return self.role.name if self.role else ''

    @property
    def permissions(self):
        if self.role:
            return self.role.permissions.all()
        return Permission.objects.none()
