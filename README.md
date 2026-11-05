# 企业OA办公系统 (Enterprise OA System)

基于 Vue3 + Django 的企业办公自动化系统，展示 AI Coding 完整开发流程。

## 技术栈

- **前端**: Vue 3 + Vite 5 + Element Plus 2.7 + Pinia
- **后端**: Django 5 + Django REST Framework + SimpleJWT
- **数据库**: SQLite

## 功能模块

- ✅ 用户权限管理（RBAC角色权限模型）
- ✅ 员工管理（部门树形结构、岗位管理）
- ✅ 审批流程（请假、报销、出差审批）
- ✅ 公告通知（发布、已读、未读统计）
- ✅ 首页仪表盘（数据统计、快捷入口）

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- npm 9+

### 一键启动

```bash
# Windows
start.bat
```

### 手动启动

**后端**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python init_data.py
python manage.py runserver 0.0.0.0:8000
```

**前端**
```bash
cd frontend
npm install
npm run dev
```

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | admin123 |
| 部门经理 | manager | manager123 |
| 普通员工 | employee | employee123 |

## 项目结构

```
enterprise-oa/
├── backend/                 # Django后端
│   ├── config/             # 项目配置
│   ├── apps/               # 业务模块
│   │   ├── users/         # 用户权限
│   │   ├── employees/     # 员工管理
│   │   ├── approvals/     # 审批流程
│   │   └── announcements/ # 公告通知
│   ├── init_data.py       # 初始化数据
│   └── manage.py          # Django管理脚本
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── views/         # 页面组件
│   │   ├── stores/        # 状态管理
│   │   └── router/        # 路由配置
│   └── index.html
├── docs/                   # 项目文档
├── AGENTS.md               # AI开发规范
├── claude.md               # 开发规范
├── start.bat              # 启动脚本
└── README.md
```

## API文档

启动后端服务后访问：
- API根路径: http://localhost:8000/api/
- 管理后台: http://localhost:8000/admin/

主要API模块：
- `/api/auth/` - 认证接口
- `/api/users/` - 用户管理
- `/api/employees/` - 员工管理
- `/api/approvals/` - 审批流程
- `/api/announcements/` - 公告通知

## 开发说明

本项目采用 **SDD（软件设计文档驱动）** + **TDD（测试驱动开发）** 模式：

1. 先编写设计文档 (docs/spec.md)
2. 再编写计划文档 (docs/plan.md)
3. 按计划逐步实现功能
4. 每个模块完成后进行测试

## 常用命令

```bash
# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic

# 加载初始数据
python init_data.py

# 前端构建
cd frontend && npm run build

# 前端预览
cd frontend && npm run preview
```

## 开发流程

详细开发流程文档请参考：
- [项目设计文档](docs/spec.md)
- [项目计划文档](docs/plan.md)
- [AI开发规范](AGENTS.md)
- [开发规范](claude.md)

## 许可证

MIT License
