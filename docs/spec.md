# 企业OA办公系统 - 项目设计文档

## 1. 项目概述

### 1.1 项目名称
Enterprise OA System（企业OA办公系统）

### 1.2 项目描述
一个基于前后端分离架构的企业办公自动化系统，提供用户权限管理、员工信息管理、审批流程、公告通知等核心功能。

### 1.3 项目目标
- 实现完整的企业OA核心功能
- 展示AI Coding的完整开发流程（SDD + TDD）
- 生成可用于博客分享的开发案例
- 代码开源至GitHub，供学习参考

### 1.4 AI的界限
**AI负责的**：
- 代码实现与调试
- 文档编写
- 配置文件生成
- 测试代码编写
- 代码重构与优化建议

**人工负责的**：
- 需求确认与变更决策
- 技术选型批准
- 业务逻辑最终确认
- 生产环境部署
- 安全审计

---

## 2. 技术架构

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────┐
│                    客户端 (Browser)                   │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/HTTPS
┌──────────────────────▼──────────────────────────────┐
│               前端 (Vue3 + Element Plus)              │
│  ┌─────────┬──────────┬───────────┬──────────────┐  │
│  │ 路由    │ 状态管理  │ API客户端  │ UI组件       │  │
│  │ Router  │ Pinia     │ Axios     │ Element Plus │  │
│  └─────────┴──────────┴───────────┴──────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │ REST API / JWT
┌──────────────────────▼──────────────────────────────┐
│              后端 (Django + DRF)                      │
│  ┌──────────┬──────────┬───────────┬─────────────┐  │
│  │ 用户权限  │ 员工管理  │ 审批流程  │ 公告通知    │  │
│  │ App      │ App      │ App      │ App         │  │
│  └──────────┴──────────┴───────────┴─────────────┘  │
│  ┌─────────────────────────────────────────────────┐ │
│  │          ORM (Django ORM)                       │ │
│  └──────────────────────┬──────────────────────────┘ │
└──────────────────────────┬──────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────┐
│                  数据库 (SQLite)                      │
└─────────────────────────────────────────────────────┘
```

### 2.2 技术栈详情

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 前端框架 | Vue | 3.x | 前端UI框架 |
| 前端构建 | Vite | 5.x | 构建工具 |
| UI组件库 | Element Plus | 2.x | 企业级UI |
| 状态管理 | Pinia | 2.x | 全局状态 |
| 路由 | Vue Router | 4.x | 前端路由 |
| HTTP客户端 | Axios | 1.x | API请求 |
| 后端框架 | Django | 5.x | Web框架 |
| API框架 | DRF | 3.x | RESTful API |
| 认证 | SimpleJWT | 5.x | JWT认证 |
| 数据库 | SQLite | 3.x | 关系型数据库 |
| Python | Python | 3.11+ | 后端语言 |
| Node.js | Node | 18+ | 前端构建 |

---

## 3. 数据库设计

### 3.1 用户权限模块

#### users_user（用户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| username | CharField(50) | 用户名，唯一 |
| password | CharField(128) | 加密密码 |
| email | CharField(100) | 邮箱，唯一 |
| phone | CharField(20) | 手机号 |
| avatar | CharField(255) | 头像URL |
| status | SmallIntegerField | 状态(0禁用/1启用) |
| role_id | FK | 外键关联角色 |
| last_login | DateTimeField | 最后登录时间 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

#### users_role（角色表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| name | CharField(50) | 角色名称，唯一 |
| code | CharField(50) | 角色编码，唯一 |
| description | TextField | 角色描述 |
| permissions | ManyToManyField | 权限列表 |
| created_at | DateTimeField | 创建时间 |

#### users_permission（权限表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| name | CharField(100) | 权限名称 |
| code | CharField(100) | 权限编码，唯一 |
| module | CharField(50) | 所属模块 |
| description | TextField | 权限描述 |

### 3.2 员工管理模块

#### employees_department（部门表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| name | CharField(100) | 部门名称 |
| code | CharField(50) | 部门编码，唯一 |
| parent_id | FK | 父部门ID（自关联） |
| manager_id | FK | 部门负责人（关联用户） |
| sort | IntegerField | 排序号 |
| created_at | DateTimeField | 创建时间 |

#### employees_position（岗位表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| name | CharField(50) | 岗位名称 |
| code | CharField(50) | 岗位编码，唯一 |
| description | TextField | 岗位描述 |

#### employees_employee（员工表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| employee_no | CharField(20) | 工号，唯一 |
| name | CharField(50) | 姓名 |
| gender | SmallIntegerField | 性别(0女/1男) |
| id_card | CharField(18) | 身份证号 |
| phone | CharField(20) | 手机号 |
| email | CharField(100) | 邮箱 |
| department_id | FK | 所属部门 |
| position_id | FK | 岗位 |
| entry_date | DateField | 入职日期 |
| status | SmallIntegerField | 状态(0离职/1在职) |
| user_id | OneToOneField | 关联系统用户 |
| created_at | DateTimeField | 创建时间 |

### 3.3 审批流程模块

#### approvals_approval_type（审批类型表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| name | CharField(50) | 审批名称 |
| code | CharField(50) | 审批编码，唯一 |
| description | TextField | 审批描述 |
| fields | JSONField | 表单字段配置 |
| approvers | JSONField | 审批人配置 |
| created_at | DateTimeField | 创建时间 |

#### approvals_approval（审批单表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| type_id | FK | 审批类型 |
| title | CharField(200) | 审批标题 |
| content | JSONField | 审批内容（动态表单） |
| applicant_id | FK | 申请人 |
| status | CharField(20) | 状态(pending/approved/rejected/revoked) |
| current_approver_id | FK | 当前审批人 |
| created_at | DateTimeField | 申请时间 |
| updated_at | DateTimeField | 更新时间 |

#### approvals_approval_record（审批记录表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| approval_id | FK | 关联审批单 |
| approver_id | FK | 审批人 |
| action | CharField(20) | 操作(approve/reject/cc) |
| comment | TextField | 审批意见 |
| created_at | DateTimeField | 操作时间 |

### 3.4 公告通知模块

#### announcements_announcement（公告表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| title | CharField(200) | 公告标题 |
| content | TextField | 公告内容 |
| publisher_id | FK | 发布人 |
| department_id | FK | 发布部门 |
| priority | SmallIntegerField | 优先级(1普通/2重要/3紧急) |
| status | SmallIntegerField | 状态(0草稿/1已发布/2已撤回) |
| published_at | DateTimeField | 发布时间 |
| created_at | DateTimeField | 创建时间 |

#### announcements_announcement_read（公告已读记录表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| announcement_id | FK | 关联公告 |
| user_id | FK | 阅读用户 |
| read_at | DateTimeField | 阅读时间 |

---

## 4. API设计

### 4.1 认证API
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login/ | 用户登录 |
| POST | /api/auth/refresh/ | 刷新Token |
| POST | /api/auth/logout/ | 用户登出 |
| GET | /api/auth/profile/ | 获取当前用户信息 |
| PUT | /api/auth/profile/ | 更新当前用户信息 |

### 4.2 用户管理API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/users/ | 用户列表 |
| POST | /api/users/ | 创建用户 |
| GET | /api/users/{id}/ | 用户详情 |
| PUT | /api/users/{id}/ | 更新用户 |
| DELETE | /api/users/{id}/ | 删除用户 |
| GET | /api/users/roles/ | 角色列表 |
| POST | /api/users/roles/ | 创建角色 |
| GET | /api/users/permissions/ | 权限列表 |

### 4.3 员工管理API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/employees/ | 员工列表 |
| POST | /api/employees/ | 创建员工 |
| GET | /api/employees/{id}/ | 员工详情 |
| PUT | /api/employees/{id}/ | 更新员工 |
| DELETE | /api/employees/{id}/ | 删除员工 |
| GET | /api/employees/departments/ | 部门列表 |
| POST | /api/employees/departments/ | 创建部门 |
| GET | /api/employees/positions/ | 岗位列表 |
| POST | /api/employees/positions/ | 创建岗位 |

### 4.4 审批流程API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/approvals/types/ | 审批类型列表 |
| POST | /api/approvals/types/ | 创建审批类型 |
| GET | /api/approvals/ | 审批单列表（我发起的） |
| POST | /api/approvals/ | 创建审批单 |
| GET | /api/approvals/{id}/ | 审批单详情 |
| POST | /api/approvals/{id}/approve/ | 审批通过 |
| POST | /api/approvals/{id}/reject/ | 审批驳回 |
| GET | /api/approvals/pending/ | 待我审批列表 |
| GET | /api/approvals/{id}/records/ | 审批记录 |

### 4.5 公告通知API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/announcements/ | 公告列表 |
| POST | /api/announcements/ | 创建公告 |
| GET | /api/announcements/{id}/ | 公告详情 |
| PUT | /api/announcements/{id}/ | 更新公告 |
| POST | /api/announcements/{id}/publish/ | 发布公告 |
| POST | /api/announcements/{id}/revoke/ | 撤回公告 |
| POST | /api/announcements/{id}/read/ | 标记已读 |
| GET | /api/announcements/unread/ | 未读公告数量 |

---

## 5. 前端页面设计

### 5.1 页面结构
```
├── 登录页 (Login)
├── 主页 (Layout)
│   ├── 首页工作台 (Dashboard)
│   ├── 用户管理
│   │   ├── 用户列表
│   │   ├── 角色管理
│   │   └── 权限配置
│   ├── 员工管理
│   │   ├── 员工列表
│   │   ├── 部门管理
│   │   └── 岗位管理
│   ├── 审批流程
│   │   ├── 发起审批
│   │   ├── 我的审批
│   │   ├── 待我审批
│   │   └── 审批类型配置
│   ├── 公告通知
│   │   ├── 公告列表
│   │   └── 发布公告
│   └── 个人中心
│       ├── 个人信息
│       └── 修改密码
```

### 5.2 路由配置
| 路径 | 组件 | 权限 | 说明 |
|------|------|------|------|
| /login | Login | 公开 | 登录页 |
| / | Layout | 登录 | 主框架 |
| /dashboard | Dashboard | 登录 | 首页 |
| /users/list | UserList | 用户管理 | 用户列表 |
| /users/roles | RoleList | 用户管理 | 角色列表 |
| /employees/list | EmployeeList | 员工管理 | 员工列表 |
| /employees/departments | DepartmentList | 员工管理 | 部门管理 |
| /employees/positions | PositionList | 员工管理 | 岗位管理 |
| /approvals/create | ApprovalCreate | 审批发起 | 发起审批 |
| /approvals/mine | ApprovalMine | 审批查看 | 我的审批 |
| /approvals/pending | ApprovalPending | 审批审批 | 待我审批 |
| /approvals/types | ApprovalTypeList | 审批配置 | 审批类型 |
| /announcements/list | AnnouncementList | 公告查看 | 公告列表 |
| /announcements/create | AnnouncementCreate | 公告发布 | 发布公告 |
| /profile | Profile | 登录 | 个人中心 |

---

## 6. 项目规范

### 6.1 代码规范
- 前端：遵循Vue3 Composition API规范
- 后端：遵循PEP8 Python编码规范
- 注释：关键代码需要添加中文注释

### 6.2 Git规范
- 分支模型：main / develop / feature/* / hotfix/*
- 提交信息格式：`<type>: <description>`
- 类型：feat / fix / docs / style / refactor / test / chore

### 6.3 目录规范
```
enterprise-oa/
├── backend/                 # 后端项目
│   ├── config/             # 项目配置
│   ├── apps/               # 业务模块
│   │   ├── users/         # 用户权限
│   │   ├── employees/     # 员工管理
│   │   ├── approvals/     # 审批流程
│   │   └── announcements/ # 公告通知
│   └── utils/              # 工具函数
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── assets/        # 静态资源
│   │   ├── components/    # 公共组件
│   │   ├── layouts/       # 布局组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   ├── utils/         # 工具函数
│   │   └── views/         # 页面视图
│   └── public/            # 公共资源
├── docs/                   # 项目文档
└── scripts/               # 脚本文件
```

---

## 7. 初始数据

### 7.1 默认管理员
- 用户名：admin
- 密码：admin123
- 角色：超级管理员

### 7.2 默认角色
| 角色 | 编码 | 说明 |
|------|------|------|
| 超级管理员 | SUPER_ADMIN | 拥有所有权限 |
| 部门经理 | DEPARTMENT_MANAGER | 管理本部门 |
| 普通员工 | EMPLOYEE | 基本操作权限 |

### 7.3 默认权限
按模块划分的基础权限：
- 用户管理：查看、创建、编辑、删除
- 员工管理：查看、创建、编辑、删除
- 审批流程：发起、审批、查看
- 公告通知：发布、编辑、撤回、查看
