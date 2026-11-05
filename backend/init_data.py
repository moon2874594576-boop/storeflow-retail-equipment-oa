import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, Role, Permission
from apps.employees.models import Department, Position, Employee

def init_permissions():
    """初始化权限数据"""
    permissions_data = [
        # 用户管理权限
        {'name': '查看用户', 'code': 'user_view', 'module': '用户管理'},
        {'name': '创建用户', 'code': 'user_create', 'module': '用户管理'},
        {'name': '编辑用户', 'code': 'user_edit', 'module': '用户管理'},
        {'name': '删除用户', 'code': 'user_delete', 'module': '用户管理'},
        {'name': '角色管理', 'code': 'role_manage', 'module': '用户管理'},
        # 员工管理权限
        {'name': '查看员工', 'code': 'employee_view', 'module': '员工管理'},
        {'name': '创建员工', 'code': 'employee_create', 'module': '员工管理'},
        {'name': '编辑员工', 'code': 'employee_edit', 'module': '员工管理'},
        {'name': '删除员工', 'code': 'employee_delete', 'module': '员工管理'},
        {'name': '部门管理', 'code': 'department_manage', 'module': '员工管理'},
        {'name': '岗位管理', 'code': 'position_manage', 'module': '员工管理'},
        # 审批流程权限
        {'name': '发起审批', 'code': 'approval_create', 'module': '审批流程'},
        {'name': '查看审批', 'code': 'approval_view', 'module': '审批流程'},
        {'name': '审批处理', 'code': 'approval_handle', 'module': '审批流程'},
        {'name': '审批配置', 'code': 'approval_config', 'module': '审批流程'},
        # 公告通知权限
        {'name': '查看公告', 'code': 'announcement_view', 'module': '公告通知'},
        {'name': '发布公告', 'code': 'announcement_create', 'module': '公告通知'},
        {'name': '编辑公告', 'code': 'announcement_edit', 'module': '公告通知'},
        {'name': '撤回公告', 'code': 'announcement_revoke', 'module': '公告通知'},
    ]
    
    for data in permissions_data:
        Permission.objects.get_or_create(code=data['code'], defaults=data)
    print(f'✅ 初始化权限完成，共 {Permission.objects.count()} 条')

def init_roles():
    """初始化角色数据"""
    roles_data = [
        {
            'name': '超级管理员',
            'code': 'SUPER_ADMIN',
            'description': '拥有系统所有权限',
        },
        {
            'name': '部门经理',
            'code': 'DEPARTMENT_MANAGER',
            'description': '管理本部门员工和审批',
        },
        {
            'name': '普通员工',
            'code': 'EMPLOYEE',
            'description': '基本操作权限',
        },
    ]
    
    for data in roles_data:
        Role.objects.get_or_create(code=data['code'], defaults=data)
    
    # 为超级管理员分配所有权限
    super_admin = Role.objects.get(code='SUPER_ADMIN')
    super_admin.permissions.set(Permission.objects.all())
    
    # 为部门经理分配相关权限
    manager = Role.objects.get(code='DEPARTMENT_MANAGER')
    manager_permissions = Permission.objects.filter(
        code__in=['user_view', 'employee_view', 'employee_create', 'employee_edit',
                  'employee_delete', 'department_manage', 'position_manage',
                  'approval_create', 'approval_view', 'approval_handle',
                  'announcement_view', 'announcement_create', 'announcement_edit']
    )
    manager.permissions.set(manager_permissions)
    
    # 为普通员工分配基础权限
    employee = Role.objects.get(code='EMPLOYEE')
    employee_permissions = Permission.objects.filter(
        code__in=['user_view', 'employee_view', 'approval_create', 'approval_view',
                  'announcement_view']
    )
    employee.permissions.set(employee_permissions)
    
    print(f'✅ 初始化角色完成，共 {Role.objects.count()} 个角色')

def init_departments():
    """初始化部门数据"""
    departments_data = [
        {'name': '总经办', 'code': 'CEO', 'sort': 1},
        {'name': '技术部', 'code': 'TECH', 'sort': 2},
        {'name': '产品部', 'code': 'PRODUCT', 'sort': 3},
        {'name': '市场部', 'code': 'MARKET', 'sort': 4},
        {'name': '人力资源部', 'code': 'HR', 'sort': 5},
        {'name': '财务部', 'code': 'FINANCE', 'sort': 6},
    ]
    
    dept_map = {}
    for data in departments_data:
        dept, created = Department.objects.get_or_create(code=data['code'], defaults=data)
        dept_map[data['code']] = dept
    
    # 设置子部门
    sub_departments = [
        {'name': '前端组', 'code': 'TECH_FRONTEND', 'parent': 'TECH', 'sort': 1},
        {'name': '后端组', 'code': 'TECH_BACKEND', 'parent': 'TECH', 'sort': 2},
        {'name': '测试组', 'code': 'TECH_TEST', 'parent': 'TECH', 'sort': 3},
        {'name': 'UI设计组', 'code': 'PRODUCT_UI', 'parent': 'PRODUCT', 'sort': 1},
        {'name': '产品规划组', 'code': 'PRODUCT_PLAN', 'parent': 'PRODUCT', 'sort': 2},
    ]
    
    for data in sub_departments:
        parent = dept_map.get(data['parent'])
        dept, created = Department.objects.get_or_create(
            code=data['code'],
            defaults={**data, 'parent': parent}
        )
        dept_map[data['code']] = dept
    
    print(f'✅ 初始化部门完成，共 {Department.objects.count()} 个部门')
    return dept_map

def init_positions():
    """初始化岗位数据"""
    positions_data = [
        {'name': '总经理', 'code': 'CEO', 'description': '公司最高负责人'},
        {'name': '技术总监', 'code': 'CTO', 'description': '技术部门负责人'},
        {'name': '产品总监', 'code': 'CPO', 'description': '产品部门负责人'},
        {'name': '市场总监', 'code': 'CMO', 'description': '市场部门负责人'},
        {'name': '项目经理', 'code': 'PM', 'description': '项目管理'},
        {'name': '前端工程师', 'code': 'FE_DEV', 'description': '前端开发'},
        {'name': '后端工程师', 'code': 'BE_DEV', 'description': '后端开发'},
        {'name': '测试工程师', 'code': 'QA', 'description': '质量保证'},
        {'name': 'UI设计师', 'code': 'UI_DESIGNER', 'description': '界面设计'},
        {'name': '产品经理', 'code': 'PRODUCT_MANAGER', 'description': '产品规划'},
        {'name': '人事经理', 'code': 'HR_MANAGER', 'description': '人力资源'},
        {'name': '财务经理', 'code': 'FINANCE_MANAGER', 'description': '财务管理'},
        {'name': '行政专员', 'code': 'ADMIN', 'description': '行政事务'},
    ]
    
    for data in positions_data:
        Position.objects.get_or_create(code=data['code'], defaults=data)
    
    print(f'✅ 初始化岗位完成，共 {Position.objects.count()} 个岗位')

def init_users():
    """初始化用户数据"""
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@company.com',
            'phone': '13800000000',
            'password': 'admin123',
            'role': 'SUPER_ADMIN',
            'status': 1,
            'is_staff': True,
        },
        {
            'username': 'manager',
            'email': 'manager@company.com',
            'phone': '13800000001',
            'password': 'manager123',
            'role': 'DEPARTMENT_MANAGER',
            'status': 1,
        },
        {
            'username': 'employee',
            'email': 'employee@company.com',
            'phone': '13800000002',
            'password': 'employee123',
            'role': 'EMPLOYEE',
            'status': 1,
        },
    ]
    
    for data in users_data:
        role_code = data.pop('role')
        password = data.pop('password')
        role = Role.objects.get(code=role_code)
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={**data, 'role': role}
        )
        # 无论新建还是已存在，都重新设置密码（确保加密）
        user.set_password(password)
        user.email = data['email']
        user.phone = data['phone']
        user.status = data['status']
        user.role = role
        if data.get('is_staff'):
            user.is_staff = data['is_staff']
        user.save()
    
    print(f'✅ 初始化用户完成，共 {User.objects.count()} 个用户')

def init_employees():
    """初始化员工数据"""
    employees_data = [
        {
            'employee_no': 'E001',
            'name': '超级管理员',
            'gender': 1,
            'phone': '13800000000',
            'email': 'admin@company.com',
            'department': 'CEO',
            'position': 'CEO',
            'entry_date': '2024-01-01',
            'status': 1,
            'user': 'admin',
        },
        {
            'employee_no': 'E002',
            'name': '部门经理',
            'gender': 1,
            'phone': '13800000001',
            'email': 'manager@company.com',
            'department': 'TECH',
            'position': 'CTO',
            'entry_date': '2024-03-15',
            'status': 1,
            'user': 'manager',
        },
        {
            'employee_no': 'E003',
            'name': '普通员工',
            'gender': 0,
            'phone': '13800000002',
            'email': 'employee@company.com',
            'department': 'TECH_FRONTEND',
            'position': 'FE_DEV',
            'entry_date': '2024-06-01',
            'status': 1,
            'user': 'employee',
        },
        {
            'employee_no': 'E004',
            'name': '张三',
            'gender': 1,
            'phone': '13900000001',
            'email': 'zhangsan@company.com',
            'department': 'TECH_BACKEND',
            'position': 'BE_DEV',
            'entry_date': '2024-02-01',
            'status': 1,
        },
        {
            'employee_no': 'E005',
            'name': '李四',
            'gender': 1,
            'phone': '13900000002',
            'email': 'lisi@company.com',
            'department': 'TECH_TEST',
            'position': 'QA',
            'entry_date': '2024-04-10',
            'status': 1,
        },
        {
            'employee_no': 'E006',
            'name': '王五',
            'gender': 0,
            'phone': '13900000003',
            'email': 'wangwu@company.com',
            'department': 'PRODUCT_UI',
            'position': 'UI_DESIGNER',
            'entry_date': '2024-05-20',
            'status': 1,
        },
        {
            'employee_no': 'E007',
            'name': '赵六',
            'gender': 1,
            'phone': '13900000004',
            'email': 'zhaoliu@company.com',
            'department': 'MARKET',
            'position': 'PM',
            'entry_date': '2024-07-01',
            'status': 1,
        },
    ]
    
    for data in employees_data:
        dept_code = data.pop('department')
        pos_code = data.pop('position')
        username = data.pop('user', None)
        
        department = Department.objects.get(code=dept_code)
        position = Position.objects.get(code=pos_code)
        user = User.objects.get(username=username) if username else None
        
        Employee.objects.get_or_create(
            employee_no=data['employee_no'],
            defaults={**data, 'department': department, 'position': position, 'user': user}
        )
    
    print(f'✅ 初始化员工完成，共 {Employee.objects.count()} 个员工')

def init_approval_types():
    """初始化审批类型数据"""
    from apps.approvals.models import ApprovalType
    
    approval_types = [
        {
            'name': '请假申请',
            'code': 'LEAVE',
            'description': '员工请假审批',
            'fields': [
                {'key': 'leave_type', 'label': '请假类型', 'type': 'select', 
                 'options': ['年假', '事假', '病假', '婚假', '产假', '陪产假']},
                {'key': 'start_date', 'label': '开始日期', 'type': 'date'},
                {'key': 'end_date', 'label': '结束日期', 'type': 'date'},
                {'key': 'reason', 'label': '请假原因', 'type': 'textarea'},
            ],
            'approvers': [2],  # 部门经理
        },
        {
            'name': '报销申请',
            'code': 'EXPENSE',
            'description': '费用报销审批',
            'fields': [
                {'key': 'expense_type', 'label': '报销类型', 'type': 'select',
                 'options': ['差旅费', '招待费', '办公费', '培训费', '其他']},
                {'key': 'amount', 'label': '金额', 'type': 'number'},
                {'key': 'description', 'label': '费用说明', 'type': 'textarea'},
            ],
            'approvers': [2],
        },
        {
            'name': '出差申请',
            'code': 'TRAVEL',
            'description': '出差审批',
            'fields': [
                {'key': 'destination', 'label': '目的地', 'type': 'text'},
                {'key': 'purpose', 'label': '出差目的', 'type': 'textarea'},
                {'key': 'start_date', 'label': '开始日期', 'type': 'date'},
                {'key': 'end_date', 'label': '结束日期', 'type': 'date'},
                {'key': 'budget', 'label': '预计费用', 'type': 'number'},
            ],
            'approvers': [2],
        },
    ]
    
    for data in approval_types:
        ApprovalType.objects.get_or_create(code=data['code'], defaults=data)
    
    from apps.approvals.models import ApprovalType
    print(f'✅ 初始化审批类型完成，共 {ApprovalType.objects.count()} 个类型')

def main():
    print('=' * 50)
    print('开始初始化企业OA系统数据...')
    print('=' * 50)
    
    try:
        init_permissions()
        init_roles()
        dept_map = init_departments()
        init_positions()
        init_users()
        init_employees()
        init_approval_types()
        
        print('=' * 50)
        print('🎉 数据初始化完成！')
        print('=' * 50)
        print('\n默认账号：')
        print('  超级管理员: admin / admin123')
        print('  部门经理: manager / manager123')
        print('  普通员工: employee / employee123')
        print('')
        
    except Exception as e:
        print(f'❌ 初始化失败: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
