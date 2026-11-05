# 运行、部署与数据恢复

## Windows / PyCharm 日常演示

推荐 Python 3.12。在 PyCharm 新建虚拟环境，安装根目录 requirements.txt，运行根目录 main.py。服务仅监听本机 127.0.0.1:8765，前端和接口同源。`frontend/dist` 已随源码提供，日常无需 npm。

如果 PyCharm 终端的 python 与 Run 使用的解释器不同，用 Run 配置显示的解释器执行 pip；不要只给另一个 Python 安装依赖。启动后控制台输出解释器相关错误、项目地址和数据目录。

支持的参数：`--port 8766`、`--no-browser`、`--check`。`--check` 会迁移数据库并在演示模式下补充演示数据，然后执行 Django 检查，不启动 HTTP 服务。

| 环境变量 | 作用 |
|---|---|
| `STOREFLOW_DATA_DIR` | 本机数据目录，默认项目 runtime |
| `STOREFLOW_DB_PATH` | SQLite 文件路径，默认 runtime/storeflow.sqlite3 |
| `DATABASE_URL` | PostgreSQL 连接 URL；设置后使用 PostgreSQL |
| `STOREFLOW_SECRET_KEY` | 签名密钥；main.py 未显式设置时使用 runtime/secret.key |
| `STOREFLOW_DEMO` | 是否初始化虚构演示数据，1 或 0 |
| `STOREFLOW_DEMO_PASSWORD` | 首次创建演示账号时的密码，默认 Demo2026! |
| `STOREFLOW_DEBUG` | Django 调试开关，交付演示默认关闭 |
| `STOREFLOW_ALLOWED_HOSTS` | 允许的请求主机名，英文逗号分隔 |

在 PyCharm Run Configuration 的 Environment variables 中设置变量。`.env` 示例专供 Docker Compose，不能据此假设 PyCharm 自动读取该文件。

## Docker Compose / PostgreSQL 16

需要 Docker Engine 或 Docker Desktop 的 Linux containers 功能。Windows 初次安装 Docker Desktop 时，先按官方要求配置虚拟化与 WSL 2。未成功运行的容器步骤不得记为通过。

首次运行：

```powershell
Copy-Item .env.example .env
# 编辑 .env：将 POSTGRES_PASSWORD 换成自己的本地密码
docker compose up -d --build --wait
docker compose ps
```

密码建议使用足够长的字母数字组合，避免未经 URL 编码的 @、/、# 等分隔字符。Compose 仅发布到 127.0.0.1:8765，数据库不对外发布端口。浏览器地址与本机运行相同。已有 .env 时编辑现有文件。

容器启动使用 Waitress，不运行 Django 开发服务器。前端在构建阶段生成，镜像以非 root 账号运行；PostgreSQL 数据与应用密钥目录使用独立数据卷。Compose 明确开启虚构演示模式，供本机学习用途。

```powershell
docker compose logs --tail 100 app
docker compose restart app
docker compose up -d --force-recreate --wait app
docker compose stop
```

以上重启和重建应用操作保留数据卷。不要在需要保留数据时使用删除数据卷的命令。每次启动的 seed_demo 为幂等初始化，不能覆盖已修改的申请或重置已有用户密码。

## SQLite 一致性备份与新文件恢复

```powershell
python scripts/backup.py --output backups/interview.sqlite3
python scripts/restore.py --input backups/interview.sqlite3 --target runtime/restored.sqlite3
python scripts/database_snapshot.py
python scripts/database_snapshot.py --file runtime/restored.sqlite3
```

backup 使用 SQLite backup API，读取一致性快照，包含 WAL 已提交内容；每份文件执行 integrity 检查。目标已存在则拒绝操作，不会覆盖正在使用的文件。snapshot 输出每个业务表的行数和内容摘要，供恢复前后比较；不输出业务明文。

检查恢复文件后停止应用，在 PyCharm 设置 `STOREFLOW_DB_PATH` 为恢复文件的绝对路径，再运行。保留原文件作为回退。签名密钥另行保留在 runtime/secret.key；密钥变化会影响旧登录令牌，应重新登录。

## PostgreSQL 备份与新库恢复

应用镜像附带 PostgreSQL 16 的 pg_dump / pg_restore / createdb，无需给 Windows 额外安装客户端。

```powershell
docker compose exec app python scripts/backup.py --output /app/runtime/interview.dump
docker compose exec app python scripts/restore.py --input /app/runtime/interview.dump --database storeflow_restored
docker compose exec app python scripts/database_snapshot.py
docker compose exec app python scripts/database_snapshot.py --database storeflow_restored
```

恢复会新建数据库，已存在的名字及当前活动数据库名称均会被拒绝。恢复操作需要配置的 PostgreSQL 账号具备建库权限；本机 Compose 演示账号具备该权限。若恢复失败，新库可能留存，检查错误后使用另一个新名字重试，不自动删除数据库。

snapshot 结果一致后，可以更改连接 URL 的数据库名称并重建应用，再验证登录和业务。备份文件在应用 runtime 数据卷内，可用 docker compose cp 复制出容器。日常使用时给备份起不同文件名。

## 排障练习

| 现象 | 优先检查 | 判断与处理 |
|---|---|---|
| 浏览器打不开 | PyCharm 进程、监听端口、控制台 URL | 后端未启动先处理 Python 依赖；端口占用则停止旧实例或改端口 |
| 连接数据库失败 | DATABASE_URL、Compose db 健康状态、密码 | 先验证 db ready，再检查 app 日志；不要用清空数据代替修复连接 |
| 看不到审批待办 | 当前角色、账号所属门店、申请状态 | 员工提交后才进入店长待办；另一门店无权处理 |
| 无可发放设备 | 类别、设备空闲状态、借期是否已过 | 已交接/待验收/待维修设备不能发放；修复或归还验收后再检查 |
| 401 / 登录过期 | 本机时间、令牌、账号状态 | 重新登录；停用账号不能靠旧令牌继续操作 |
| 缺少前端构建 | frontend/dist/index.html 是否存在 | 恢复仓库自带 dist，或在 frontend 执行 npm ci 和 npm run build |

维护记录请保留现象、账号、申请编号、发生时间、错误请求和修复后复测结果，避免把正常的权限拒绝当作系统故障。
