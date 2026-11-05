# claude.md - 企业OA办公系统开发规范

## 项目简介
企业OA办公系统是一个基于Vue3和Django的前后端分离项目，提供用户权限管理、员工管理、审批流程、公告通知等核心功能。

## 技术栈
- **前端**: Vue 3.4 + Vite 5 + Element Plus 2.7 + Pinia 2 + Vue Router 4
- **后端**: Django 5 + Django REST Framework 3 + SimpleJWT 5
- **数据库**: SQLite 3
- **Python**: 3.11+
- **Node.js**: 18+

## 开发环境设置

### 后端环境
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python init_data.py
python manage.py runserver 0.0.0.0:8000
```

### 前端环境
```bash
cd frontend
npm install
npm run dev  # 开发模式
npm run build  # 生产构建
```

## 代码规范

### Python/Django规范
1. 遵循 PEP8 编码规范
2. 使用 4 空格缩进
3. 行宽不超过 120 字符
4. 模型使用单数命名（User, Role, Permission）
5. 序列化器使用明确的字段定义
6. 视图继承自 ViewSet 或 APIView

### Vue.js规范
1. 使用 `<script setup>` 语法
2. 使用 Composition API
3. 组件命名使用 PascalCase
4. Props 定义类型和默认值
5. Emits 显式声明

### 文件命名
- Python文件：snake_case（如 user_serializers.py）
- Vue文件：kebab-case 或 PascalCase（如 user-list.vue 或 UserList.vue）
- 工具文件：index.js 或 utils.js

## 项目结构

### 后端结构
```
backend/
├── config/
│   ├── settings.py      # 项目配置
│   ├── urls.py          # 根路由
│   └── wsgi.py          # WSGI入口
├── apps/
│   ├── users/           # 用户权限模块
│   ├── employees/       # 员工管理模块
│   ├── approvals/       # 审批流程模块
│   └── announcements/   # 公告通知模块
├── init_data.py         # 初始化数据脚本
└── manage.py            # Django管理脚本
```

### 前端结构
```
frontend/
├── src/
│   ├── api/            # API接口封装
│   ├── layouts/        # 布局组件
│   ├── router/         # 路由配置
│   ├── stores/         # Pinia状态管理
│   ├── styles/         # 全局样式
│   ├── utils/          # 工具函数
│   └── views/          # 页面视图
│       ├── login/      # 登录页
│       ├── dashboard/  # 首页
│       ├── users/      # 用户管理
│       ├── employees/  # 员工管理
│       ├── approvals/  # 审批流程
│       ├── announcements/ # 公告通知
│       └── profile/    # 个人中心
└── index.html          # HTML入口
```

## API设计规范

### 认证
- JWT Token认证
- 请求头：`Authorization: Bearer <token>`
- Token有效期：2小时（Access）+ 7天（Refresh）

### 响应格式
- 列表：`{ count, next, previous, results: [] }`
- 详情：直接返回对象
- 错误：`{ detail: '错误信息' }`

### 分页
- 默认每页20条
- 支持 page, page_size 参数
- 支持 page, sizes, prev, pager, next, jumper 布局

## 数据库模型规范

### 字段命名
- 使用 snake_case
- 添加 verbose_name（中文注释）
- 状态字段使用 choices 定义枚举

### 关系字段
- ForeignKey：on_delete=models.SET_NULL + null=True, blank=True
- ManyToManyField：through 自定义中间表
- OneToOneField：用户与员工关联

## 样式规范
- 使用 Element Plus 组件库
- 主色调：#409EFF（Element Plus默认蓝色）
- 布局：Flexbox + Grid
- 响应式：支持 1280px+ 屏幕

## 常见问题

### Q: 如何重置数据库？
```bash
cd backend
del db.sqlite3
python manage.py migrate
python init_data.py
```

### Q: 如何创建超级管理员？
```bash
cd backend
python manage.py createsuperuser
```

### Q: 前后端联调如何配置？
前端开发服务器已配置代理，/api 请求会自动转发到 http://localhost:8000

## 部署说明
1. 运行 `start.bat` 一键启动开发环境
2. 生产环境：Django + Nginx + Gunicorn
3. 静态文件：`python manage.py collectstatic`

## 文档参考
- 设计文档：docs/spec.md
- 计划文档：docs/plan.md
