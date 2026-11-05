# AGENTS.md - 企业OA办公系统 AI开发规范

## 项目概述
- 项目名称：企业OA办公系统 (Enterprise OA System)
- 技术架构：前后端分离
- 前端：Vue3 + Element Plus
- 后端：Django + Django REST Framework
- 数据库：SQLite

## AI开发规范

### 代码风格
1. 前端代码遵循Vue3 Composition API规范
2. 后端代码遵循PEP8 Python编码规范
3. 所有关键逻辑需要添加中文注释
4. 变量和函数命名使用英文，语义清晰

### 项目结构
```
enterprise-oa/
├── backend/           # Django后端
│   ├── config/       # 项目配置
│   ├── apps/         # 业务模块
│   └── utils/        # 工具函数
├── frontend/         # Vue前端
│   ├── src/api/      # API接口
│   ├── src/views/    # 页面组件
│   └── src/stores/   # 状态管理
├── docs/             # 项目文档
└── start.bat         # 启动脚本
```

### 开发流程
1. 严格按照SDD（软件设计文档）进行开发
2. 严格遵循TDD（测试驱动开发）理念
3. 每完成一个模块进行单元测试
4. 修改代码前先阅读相关文件
5. 保持代码整洁和一致

### 安全规范
1. 不得在代码中硬编码敏感信息
2. 使用环境变量管理配置
3. 用户密码必须加密存储
4. API接口需要权限验证

### Git规范
- 分支模型：main / develop / feature/* / hotfix/*
- 提交信息格式：`<type>: <description>`
- 类型：feat / fix / docs / style / refactor / test / chore

### 数据库规范
1. 所有模型需要定义 __str__ 方法
2. 使用合适的字段类型和约束
3. 添加必要的索引以优化查询
4. 命名采用单数形式（如 User 而非 Users）

### API规范
1. 遵循RESTful API设计
2. 使用Django REST Framework的ViewSet
3. 统一的响应格式
4. 分页、过滤、搜索支持

## AI的职责
- 代码实现与调试
- 文档编写
- 配置文件生成
- 测试代码编写
- 代码重构与优化建议

## 人类的职责
- 需求确认与变更决策
- 技术选型批准
- 业务逻辑最终确认
- 生产环境部署
- 安全审计
