# group_class

拼课课程系统原型仓库，包含后端 API、前端页面、测试和实施文档。

## 项目结构

- `apps/group_class_backend/`：后端代码（课程、报名、模型、持久化、通用能力）
- `apps/group_class_frontend/`：前端页面（看板、详情、报名、后台管理）
- `tests/group_class_backend/`：后端测试
- `docs/plans/`：PRD、架构、实施计划、验收记录
- `scripts/`：本地启动/停止脚本

## 快速启动（Windows）

推荐直接使用脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1
```

默认地址：

- 前端：`http://127.0.0.1:5173/`
- 后端：`http://127.0.0.1:18000/`

停止服务：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop-local.ps1
```

## 快速启动（Linux/macOS）

```bash
chmod +x scripts/start-local.sh scripts/stop-local.sh
./scripts/start-local.sh
```

停止服务：

```bash
./scripts/stop-local.sh
```

可通过环境变量覆盖：

```bash
PYTHON_BIN=python3 FRONTEND_PORT=5173 BACKEND_PORT=18000 ./scripts/start-local.sh
```

## 容器化部署（Docker Compose）

在仓库根目录执行：

```bash
docker compose up -d --build
```

访问地址：

- 前端：`http://127.0.0.1:5173/`
- 后端：`http://127.0.0.1:18000/`

停止并删除容器：

```bash
docker compose down
```

## 测试

```bash
uv run pytest tests/ -q
```

前端语法检查：

```bash
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js
```

手动启动后端：

```bash
uv run uvicorn apps.group_class_backend.app:app --host 0.0.0.0 --port 18000 --reload
```

## 文档入口

- 部署与开发指南：`docs/development-and-deployment.md`
- 本地启动说明：`docs/local-startup-guide.md`
- 前端开发说明：`docs/frontend-startup-and-dev.md`
- 关键计划与验收：`docs/plans/2026-04-14-p0-critical-task-breakdown.md`
- 前端重设计任务：`docs/plans/2026-04-14-frontend-redesign-tasks.md`
