# SQLite Runtime 接入计划

Date: 2026-04-25
Status: Completed
Owner: Codex

## 1. 背景

当前后端已有 SQLite schema 和 repository 测试覆盖，但 `apps/group_class_backend/server.py` runtime 仍固定使用 InMemory repository。服务重启后课程和报名数据会丢失，影响本地演示和后续联调。

## 2. 范围

计划修改：

- `apps/group_class_backend/server.py`
- `apps/group_class_backend/persistence/schema.py`
- 后端 server runtime 相关测试
- 当前进度文档

不处理：

- 正式迁移框架，例如 Alembic
- 生产级用户体系和 token 持久化
- 审计日志持久化
- 前端分页、搜索、筛选

## 3. 设计

新增环境变量：

- `GROUP_CLASS_STORAGE`
  - 默认：`memory`
  - 可选：`sqlite`
- `GROUP_CLASS_SQLITE_PATH`
  - SQLite 文件路径
  - 默认：`.runtime/group_class.sqlite3`

行为：

- 默认不设置环境变量时继续使用 InMemory repository，保持兼容。
- `GROUP_CLASS_STORAGE=sqlite` 时：
  - 打开 SQLite 文件。
  - 应用 schema。
  - 使用 `SQLiteClassRepository` 和 `SQLiteRegistrationRepository`。
  - 仅当课程表为空时写入 demo seed，避免重启重复写入。
- `apply_schema()` 支持重复执行，便于 server 每次启动时确认 schema。

## 4. 验收标准

- 默认 AppState 仍使用 InMemory repository。
- `GROUP_CLASS_STORAGE=sqlite` 时 AppState 使用 SQLite repository。
- SQLite 模式下创建课程后，重新构造 AppState 仍能读取该课程。
- SQLite 模式下 `apply_schema()` 可重复执行，不因已存在的表或索引失败。
- 后端 demo seed 中文文案不再出现明显乱码。
- `python -m pytest tests/group_class_backend -q` 通过。
- 前端语法检查保持通过：
  - `node --check apps/group_class_frontend/js/api.js`
  - `node --check apps/group_class_frontend/js/app.js`

## 5. 自测记录

已执行：

- `python -m pytest tests/group_class_backend -q` -> `94 passed`
- `node --check apps/group_class_frontend/js/api.js` -> 通过
- `node --check apps/group_class_frontend/js/app.js` -> 通过
- `python -m py_compile apps/group_class_backend/server.py` -> 通过

新增自动化覆盖：

- 默认 `AppState()` 使用 InMemory repository。
- `apply_schema()` 可重复执行。
- `AppState(storage="sqlite", sqlite_path=...)` 使用 SQLite repository。
- SQLite 模式下新增课程后，重新构造 `AppState` 仍可读取该课程。

## 6. 验收结论

通过。后端 server runtime 已支持通过环境变量启用 SQLite 持久化，默认 memory 行为保持兼容。

## 7. 使用方式

默认仍使用内存：

```powershell
$env:GROUP_CLASS_BACKEND_PORT='18000'
python -m apps.group_class_backend.server
```

启用 SQLite：

```powershell
$env:GROUP_CLASS_STORAGE='sqlite'
$env:GROUP_CLASS_SQLITE_PATH='.runtime/group_class.sqlite3'
$env:GROUP_CLASS_BACKEND_PORT='18000'
python -m apps.group_class_backend.server
```

## 8. 剩余风险

- 当前仍是原型级 schema 初始化，未引入正式迁移框架。
- token 会话仍在内存中，重启后需要重新登录。
- 审计日志仍未持久化。
