# 验证记录

本记录根据2026年11月5日实际执行结果填写，技术验证与使用者本人验收分别记录。代码、配置和文档存在不能直接记作通过。

- 被测功能代码提交：[`79be8f5ec0652b8b94b087c3808c300b55dff1ed`](https://github.com/moon2874594576-boop/storeflow-retail-equipment-oa/commit/79be8f5ec0652b8b94b087c3808c300b55dff1ed)。后续文档更新与此处所指的功能代码版本区分。
- Windows / Python / Node：2026-11-05 在 Windows 11 专业版 64位、Python 3.12.5、Node 24.16.0 实测；Django 5.2.19。
- 后端测试：最终本机一轮执行33项，31项通过，2项 PostgreSQL 专用并发测试因 SQLite 环境跳过。已读取 PostgreSQL CI 实际日志，33项全部通过，无跳过。
- 真实 HTTP：scripts/verify_http.py 首轮36项断言通过，覆盖6个账号、完整损坏归还/维修、跨门店隔离、状态篡改拦截、并发分配只有一次成功、导出权限。
- 备份工具：2项独立测试通过；真实27张表备份恢复后的记录数量与内容SHA256全部一致；重复播种不改变既有记录摘要。
- 前端构建：npm run build 通过；npm audit 完整报告为0个已知漏洞。存在主前端包超过500kB的构建提示，不影响本机离线演示。
- 浏览器角色流程：实际 Playwright 浏览器中以 employee_a→manager_a→custodian→employee_a→custodian 完成一张新申请创建提交、审批、发放、签收、申请归还、正常验收；历史记录7步且设备恢复空闲。查看[完成记录与时间线](images/loan-complete.png)、[工作台](images/workbench.png)、[登录页](images/login.png)。构建过程中发现旧页面分块地址失效，已补有限次数刷新恢复；签收按钮重复文字与路由滚动位置也已修正。
- GitHub Actions：运行 [42015262422](https://github.com/moon2874594576-boop/storeflow-retail-equipment-oa/actions/runs/42015262422) 的四项任务全部成功：Windows原生、Linux原生、PostgreSQL 16测试，以及真实Docker容器验证。本机SQLite跳过的两项PostgreSQL专用并发测试由该PostgreSQL任务实际执行。容器任务运行了真实HTTP验收、PostgreSQL备份与新库恢复、应用force-recreate；恢复及重建前后的表记录数量和内容摘要一致。
- GitHub下载版复验：从GitHub codeload下载上述提交对应源码，解压145个文件至 `D:\SoftwareforDestop\ProgrammingLanguage\Python\GitHub\Program3`，在该目录建立独立 `.venv` 并成功安装依赖。从无关工作目录以绝对路径运行此下载版 `main.py`，Waitress成功监听本机8765端口；下载版真实HTTP验收36项断言全部通过，验收申请编号为 `SF202611050CEC19DC5B`。此结果来自下载版自身，不沿用开发目录的虚拟环境。
- 最终入口与下载：提交 `3239f6740cae753b633ff521ada667920bad2357` 统一了Windows启动脚本，并停用上游旧初始化入口。其 [CI 42016960303](https://github.com/moon2874594576-boop/storeflow-retail-equipment-oa/actions/runs/42016960303) 四项全部成功；重新从GitHub下载并逐一核对全部跟踪文件（批处理按Git属性规范化CRLF换行），保留本机虚拟环境和数据。下载版 `start.bat --check` 与 `pip check` 通过。
- PyCharm内操作：最初由Codex启动IDE报 `DirectoryLock` / `SocketException: Invalid argument: bind`，后按[JetBrains官方建议](https://youtrack.jetbrains.com/articles/SUPPORT-A-1204/IDE-crashes-SocketException-Invalid-argument-bind)从Windows资源管理器直接启动，未修改IDE全局配置。实际在PyCharm 2024.2.1新窗口打开Program3，自动识别其 `.venv` Python 3.12解释器，打开根目录 `main.py` 并执行Run。运行进程父级为PyCharm，浏览器自动打开，健康检查返回200。切换至IDE运行前后的27张表数量和内容摘要完全一致；针对IDE启动的服务再执行真实HTTP36项断言全部通过，申请号 `SF20261105C86076C650`。查看[IDE运行截图](images/pycharm-run.png)。
- 本人验收：仍待使用者按[演示与本人验收手册](demo.md)操作确认；自动化、浏览器技术验证和命令行入口运行不替代使用者本人确认。

状态使用通过、失败、未执行或待本人确认；不把未执行默认算通过。失败应关联修复和复测记录。
