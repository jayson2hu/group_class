# 后端 FastAPI 迁移开发计划

Date: 2026-04-27  
Status: Ready for Codex Execution  
Owner: Jayson  
Review: Claude  

---

## 背景与目标

将后端从手写 `http.server.ThreadingHTTPServer`（`server.py` 444 行）迁移到 FastAPI + uvicorn，引入 uv 管理依赖。

**迁移原则**
- `models/`、`classes/controller.py`、`registrations/controller.py`、`repository.py`、`persistence/schema.py`、`audit/` **一行不动**
- 现有 91 个 pytest 测试**一个不改**（它们直接调用 controller，与 HTTP 无关）
- `server.py` 迁移完成验收通过后才删除
- 不引入额外第三方库（仅 fastapi、uvicorn、httpx for tests）

**actorId/actorRoles 新设计**  
原来混在 JSON body（POST）和 query string（GET）里。迁移后统一改为 HTTP Header：
- `X-Actor-Id`：发起人 ID（默认 `u_anonymous`）
- `X-Actor-Roles`：逗号分隔的角色列表（如 `CLASS_ADMIN,INITIATOR`）

前端 `api.js` 的 `requestJson` 统一在所有请求追加这两个 header。这样：
1. 请求体只含业务字段
2. 后期换 JWT 只改 `deps.py` 中的 `get_actor`，路由和 controller 零改动

---

## 整体任务拆分

| 编号 | 任务名称 | 文件范围 | 前置 | 预估行数 |
|---|---|---|---|---|
| M1 | uv 项目初始化 + pyproject.toml | 根目录 | 无 | ~30 行 |
| M2 | FastAPI 应用骨架 + deps.py | app.py, deps.py | M1 | ~60 行 |
| M3 | classes 路由（只读） | routers/classes.py | M2 | ~80 行 |
| M4 | classes 路由（写操作 + 审核） | routers/classes.py | M3 | ~100 行 |
| M5 | registrations 路由（全部） | routers/registrations.py | M2 | ~120 行 |
| M6 | 前端 api.js Header 改造 | api.js | M2 | ~30 行改动 |
| M7 | Docker + 启动脚本更新 | Dockerfile, scripts/ | M5 | ~20 行改动 |
| M8 | 新增 API 集成测试 | tests/test_api/ | M5 | ~150 行 |
| M9 | server.py 删除 + CLAUDE.md 更新 | server.py, CLAUDE.md | M8 | 删除 + 更新 |

---

## 开发规范（Codex 必读）

### 代码规范
- Python 3.12，所有文件顶部 `from __future__ import annotations`
- 类型注解完整，不用 `Any` 除非必要
- FastAPI 路由函数用同步函数（`def`，非 `async def`）——controller 全是同步的
- 每个路由文件顶部有模块级 docstring 说明职责
- 不在路由层做业务逻辑，只做：参数解析 → 调用 controller → 返回结果

### 命名规范
- 路由文件：`apps/group_class_backend/routers/{domain}.py`
- FastAPI 入口：`apps/group_class_backend/app.py`
- 依赖注入：`apps/group_class_backend/deps.py`

### commit 规范
每个编号完成后单独 commit，格式：
```
feat(M1): uv 项目初始化，新增 pyproject.toml
feat(M2): FastAPI 应用骨架与 ActorContext 依赖注入
feat(M3): classes 只读路由迁移至 FastAPI
...
```

### 自测要求
每个任务完成后必须执行对应自测命令，截图或粘贴输出，**自测通过才算完成**。

### 验收要求
- 后端改动：`uv run pytest tests/ -q` 全部通过
- 前端改动：`node --check apps/group_class_frontend/js/api.js`
- API 改动：curl 命令验证每条路由

---

## M1：uv 项目初始化

**任务编号**：M1  
**修改文件**：`pyproject.toml`（新建）、`.python-version`（新建）  
**前置依赖**：无

### 实现内容

新建 `pyproject.toml`（项目根目录）：

```toml
[project]
name = "group-class"
version = "0.1.0"
description = "拼课课程系统后端"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]>=0.115",
    "uvicorn[standard]>=0.30",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "httpx>=0.27",
]

[tool.uv]
package = false

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

新建 `.python-version`：
```
3.12
```

新建 `.gitignore` 追加（若已有则在末尾补充）：
```
.venv/
```

### 自测命令

```bash
# 安装 uv（若未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 在项目根目录
uv sync
uv run python --version   # 期望：Python 3.12.x
uv run python -c "import fastapi; print(fastapi.__version__)"
uv run python -c "import uvicorn; print(uvicorn.__version__)"
```

### 验收标准
1. `uv sync` 无报错，生成 `uv.lock` 和 `.venv/`
2. `uv run python --version` 输出 `3.12.x`
3. fastapi 和 uvicorn 可正常 import
4. `uv.lock` 文件已生成（提交到 git）
5. `.venv/` 在 `.gitignore` 中

---

## M2：FastAPI 应用骨架 + deps.py

**任务编号**：M2  
**修改文件**：`apps/group_class_backend/app.py`（新建）、`apps/group_class_backend/deps.py`（新建）  
**前置依赖**：M1

### apps/group_class_backend/deps.py

```python
from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import Header


@dataclass(frozen=True)
class ActorContext:
    actor_id: str
    actor_roles: list[str] = field(default_factory=list)


def get_actor(
    x_actor_id: str = Header(default="u_anonymous"),
    x_actor_roles: str = Header(default=""),
) -> ActorContext:
    roles = [r.strip() for r in x_actor_roles.split(",") if r.strip()]
    return ActorContext(actor_id=x_actor_id, actor_roles=roles)
```

### apps/group_class_backend/app.py

```python
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.group_class_backend.audit.interface import NullAuditWriter
from apps.group_class_backend.classes.repository import InMemoryClassRepository
from apps.group_class_backend.common.enums import ClassStatus
from apps.group_class_backend.models.group_class import GroupClass
from apps.group_class_backend.registrations.repository import InMemoryRegistrationRepository


class AppState:
    def __init__(self) -> None:
        self.class_repository = InMemoryClassRepository()
        self.registration_repository = InMemoryRegistrationRepository()
        self.audit_writer = NullAuditWriter()
        _seed_classes(self.class_repository)


# 全局单例，lifespan 中初始化
_state: AppState | None = None


def get_state() -> AppState:
    assert _state is not None
    return _state


def _seed_classes(repo: InMemoryClassRepository) -> None:
    # 与 server.py 保持一致的种子数据，此处省略实现——
    # Codex 请直接复制 server.py 中 _seed_classes 函数的全部内容
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _state
    _state = AppState()
    yield


app = FastAPI(
    title="拼课课程系统",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由在 M3/M4/M5 中注册，此处预留
# from apps.group_class_backend.routers import classes, registrations
# app.include_router(classes.router)
# app.include_router(registrations.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("GROUP_CLASS_BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("GROUP_CLASS_BACKEND_PORT", "18000"))
    uvicorn.run("apps.group_class_backend.app:app", host=host, port=port, reload=False)
```

**注意**：`_seed_classes` 函数请完整复制 `server.py` 第 37-110 行内容（三个种子课程），不要省略。

### 自测命令

```bash
uv run uvicorn apps.group_class_backend.app:app --host 127.0.0.1 --port 18000
# 新开终端
curl http://127.0.0.1:18000/health
# 期望：{"status":"ok"}
curl http://127.0.0.1:18000/docs
# 期望：200 返回 Swagger UI HTML
```

### 验收标准
1. `GET /health` 返回 `{"status": "ok"}`
2. `GET /docs` 可访问 Swagger UI
3. 应用启动无报错
4. CORS 头存在：`curl -I http://127.0.0.1:18000/health` 含 `access-control-allow-origin: *`

---

## M3：classes 只读路由

**任务编号**：M3  
**修改文件**：`apps/group_class_backend/routers/classes.py`（新建）、`apps/group_class_backend/routers/__init__.py`（新建）、`app.py`（注册路由）  
**前置依赖**：M2

### 接口列表（本任务）

| 方法 | 路径 | controller 函数 |
|---|---|---|
| GET | `/api/v1/public/classes` | `list_classes(public_only=True)` |
| GET | `/api/v1/public/classes/{class_id}` | `get_class_detail(public_only=True)` |
| GET | `/api/v1/admin/classes` | `list_classes(public_only=False)` |
| GET | `/api/v1/admin/classes/{class_id}` | `get_class_detail(public_only=False)` |

### 实现要点

```python
# apps/group_class_backend/routers/classes.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from datetime import datetime, timezone

from apps.group_class_backend.app import get_state
from apps.group_class_backend.classes.controller import (
    get_class_detail,
    list_classes,
)
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.deps import ActorContext, get_actor

router = APIRouter()


def _http_status(result: dict, fallback: int = 400) -> int:
    code = result.get("code")
    if code == ErrorCode.OK.value:
        return 200
    if code == ErrorCode.CLASS_NOT_FOUND.value:
        return 404
    if code == ErrorCode.PERMISSION_DENIED.value:
        return 403
    if code == ErrorCode.CLASS_VERSION_CONFLICT.value:
        return 409
    return fallback


@router.get("/api/v1/public/classes")
def public_list_classes(page: int = 1, page_size: int = 20):
    state = get_state()
    result = list_classes(
        repository=state.class_repository,
        request_id=_new_request_id(),
        page=page,
        page_size=min(page_size, 100),
        public_only=True,
    )
    return result


# 其余路由同理，Codex 请按此模式实现全部 4 条路由
```

`_new_request_id()` 辅助函数：
```python
from uuid import uuid4
def _new_request_id() -> str:
    return f"req-{uuid4().hex[:12]}"
```

在 `app.py` 中注册（取消注释）：
```python
from apps.group_class_backend.routers import classes as classes_router
app.include_router(classes_router.router)
```

### 自测命令

```bash
uv run uvicorn apps.group_class_backend.app:app --host 127.0.0.1 --port 18000

# 前台课程列表
curl http://127.0.0.1:18000/api/v1/public/classes
# 期望：{"requestId":"...","code":"OK","data":{"page":1,"pageSize":20,"total":2,"items":[...]}}

# 前台课程详情
curl http://127.0.0.1:18000/api/v1/public/classes/{classId}
# 期望：200，含课程详情

# 不存在的课程
curl -w "\nHTTP:%{http_code}" http://127.0.0.1:18000/api/v1/public/classes/not-exist
# 期望：HTTP:404

# 后台列表（含 DRAFT）
curl http://127.0.0.1:18000/api/v1/admin/classes
# 期望：items 包含 3 条（含草稿）
```

### 验收标准
1. `GET /api/v1/public/classes` 返回 200，items 含 2 条公开课程（OPEN_FOR_ENROLLMENT + FULL）
2. `GET /api/v1/admin/classes` 返回 3 条（含 DRAFT）
3. 不存在的 classId 返回 404
4. 响应格式与旧 server.py 完全一致（`{requestId, code, data}`）
5. `uv run pytest tests/group_class_backend -q` 仍全部通过

---

## M4：classes 写操作 + 审核路由

**任务编号**：M4  
**修改文件**：`apps/group_class_backend/routers/classes.py`（追加）  
**前置依赖**：M3

### 接口列表（本任务）

| 方法 | 路径 | controller 函数 | actorId 来源 |
|---|---|---|---|
| POST | `/api/v1/admin/classes` | `create_class_draft` | Header `X-Actor-Id` |
| POST | `/api/v1/admin/classes/{class_id}/update` | `update_class_draft` | Header `X-Actor-Id` |
| POST | `/api/v1/admin/classes/{class_id}/submit-review` | `submit_class_review` | Header `X-Actor-Id` + `X-Actor-Roles` |
| POST | `/api/v1/admin/classes/{class_id}/approve` | `approve_class_review` | Header `X-Actor-Id` + `X-Actor-Roles` |
| POST | `/api/v1/admin/classes/{class_id}/reject` | `reject_class_review` | Header `X-Actor-Id` + `X-Actor-Roles` |

### Pydantic 请求体模型

```python
from pydantic import BaseModel

class CreateClassBody(BaseModel):
    class_name: str | None = None       # API 字段名 className → 由 alias 处理
    # ... 所有字段

    model_config = {"populate_by_name": True}
```

**注意**：controller 接收的是 `dict`（原始 API 字段名，camelCase），不要在路由层做字段名转换。直接用 `body.model_dump(by_alias=True, exclude_none=True)` 传给 controller。

最简方案：请求体直接用 `dict`（`from fastapi import Body`），与旧 server.py 行为一致：

```python
from typing import Any
from fastapi import Body, Depends, Response

@router.post("/api/v1/admin/classes")
def admin_create_class(
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
    response: Response = None,
):
    state = get_state()
    result = create_class_draft(
        payload=body,
        repository=state.class_repository,
        audit_writer=state.audit_writer,
        request_id=_new_request_id(),
        actor_id=actor.actor_id,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result
```

### 自测命令

```bash
# 创建课程
curl -X POST http://127.0.0.1:18000/api/v1/admin/classes \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_test" \
  -H "X-Actor-Roles: INITIATOR" \
  -d '{"className":"FastAPI测试班","classType":"GROUP_CLASS","priceAmount":1999,"minStudents":6,"maxStudents":8}'
# 期望：200，data.status = "DRAFT"，data.classId 以 cls- 开头

# 记录返回的 classId 和 version=1

# 提交审核
curl -X POST http://127.0.0.1:18000/api/v1/admin/classes/{classId}/submit-review \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_test" \
  -H "X-Actor-Roles: INITIATOR" \
  -d '{"version":1}'
# 期望：200，data.status = "PENDING_REVIEW"

# 审核通过
curl -X POST http://127.0.0.1:18000/api/v1/admin/classes/{classId}/approve \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_admin" \
  -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"version":2}'
# 期望：200，data.status = "OPEN_FOR_ENROLLMENT"

# 无权限审核
curl -X POST http://127.0.0.1:18000/api/v1/admin/classes/{classId}/approve \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_test" \
  -H "X-Actor-Roles: INITIATOR" \
  -d '{"version":1}'
# 期望：403

# version 冲突
curl -X POST http://127.0.0.1:18000/api/v1/admin/classes/{classId}/update \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_test" \
  -d '{"version":1,"className":"冲突测试"}'
# 期望：409
```

### 验收标准
1. 创建课程成功，status = DRAFT
2. 完整审核流：DRAFT → PENDING_REVIEW → OPEN_FOR_ENROLLMENT
3. 驳回流：PENDING_REVIEW → REJECTED
4. INITIATOR 调用 approve 返回 403
5. version 不匹配返回 409
6. classId 不存在返回 404
7. `uv run pytest tests/group_class_backend -q` 全部通过

---

## M5：registrations 路由

**任务编号**：M5  
**修改文件**：`apps/group_class_backend/routers/registrations.py`（新建）、`app.py`（注册路由）  
**前置依赖**：M2

### 接口列表

| 方法 | 路径 | controller 函数 | actorId 来源 |
|---|---|---|---|
| POST | `/api/v1/public/registrations` | `submit_registration` | Header（默认 `u_public_visitor`） |
| GET | `/api/v1/admin/registrations` | `list_registrations` | Header `X-Actor-Id` + `X-Actor-Roles` |
| GET | `/api/v1/admin/registrations/{registration_id}` | `get_registration_detail` | Header |
| POST | `/api/v1/admin/registrations/{registration_id}/notes` | `update_registration_notes` | Header |
| POST | `/api/v1/admin/registrations/{registration_id}/status` | `update_registration_status` | Header |

### 实现要点

```python
@router.post("/api/v1/public/registrations")
def public_submit_registration(
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
    response: Response = None,
):
    state = get_state()
    result = submit_registration(
        payload=body,
        class_repository=state.class_repository,
        registration_repository=state.registration_repository,
        audit_writer=state.audit_writer,
        request_id=_new_request_id(),
        actor_id=actor.actor_id,
        now=datetime.now(timezone.utc),
    )
    response.status_code = 200 if result.get("code") == ErrorCode.OK.value else 400
    return result
```

### 自测命令

```bash
# 前台提交报名（需要 OPEN_FOR_ENROLLMENT 状态的课程）
# 先用 M4 创建并审核通过一个课程，记录 classId

curl -X POST http://127.0.0.1:18000/api/v1/public/registrations \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_parent_001" \
  -d '{"classId":"{classId}","registerType":"ENROLLMENT","parentName":"张三","contactInfo":"13800138000","studentName":"小明","studentGrade":"三年级","englishLevel":"基础"}'
# 期望：200，data.registrationId 以 reg- 开头

# 记录 registrationId

# 后台报名列表
curl "http://127.0.0.1:18000/api/v1/admin/registrations" \
  -H "X-Actor-Id: u_demo_creator" \
  -H "X-Actor-Roles: CLASS_ADMIN"
# 期望：200，data.items 含刚提交的记录

# 无权限列表
curl "http://127.0.0.1:18000/api/v1/admin/registrations" \
  -H "X-Actor-Id: u_parent"
# 期望：403

# 更新备注
curl -X POST "http://127.0.0.1:18000/api/v1/admin/registrations/{registrationId}/notes" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_demo_creator" \
  -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"followUpNote":"已电话确认","notes":"家长希望周三"}'
# 期望：200，data.followUpNote = "已电话确认"

# 更新状态
curl -X POST "http://127.0.0.1:18000/api/v1/admin/registrations/{registrationId}/status" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_demo_creator" \
  -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"registrationStatus":"VALID"}'
# 期望：200，data.registrationStatus = "VALID"
```

### 验收标准
1. 前台提交报名成功，返回 registrationId
2. 课程不存在/状态不对时返回 400
3. 后台报名列表无权限返回 403
4. 更新备注后内容持久（同一进程内）
5. 更新状态为非法值返回 400
6. `uv run pytest tests/group_class_backend -q` 全部通过

---

## M6：前端 api.js Header 改造

**任务编号**：M6  
**修改文件**：`apps/group_class_frontend/js/api.js`  
**前置依赖**：M2（理解新的 Header 协议即可，不依赖后端部署）

### 改造内容

**ApiClient 构造函数**增加 actorId 和 actorRoles 属性：

```javascript
export class ApiClient {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
    this.useMockData = window.localStorage.getItem("GROUP_CLASS_USE_MOCK_DATA") === "true";
    // 新增：actor 信息从 localStorage 读取，供 Header 使用
    this.actorId = window.localStorage.getItem("GROUP_CLASS_ACTOR_ID") || "u_anonymous";
    this.actorRoles = (window.localStorage.getItem("GROUP_CLASS_ACTOR_ROLES") || "")
      .split(",").map(r => r.trim()).filter(Boolean);
  }

  // 新增：刷新 actor 信息（切换角色时调用）
  refreshActor() {
    this.actorId = window.localStorage.getItem("GROUP_CLASS_ACTOR_ID") || "u_anonymous";
    this.actorRoles = (window.localStorage.getItem("GROUP_CLASS_ACTOR_ROLES") || "")
      .split(",").map(r => r.trim()).filter(Boolean);
  }
}
```

**`requestJson` 函数**统一追加 Header：

```javascript
async function requestJson(url, options = {}, actorId = "u_anonymous", actorRoles = []) {
  const headers = {
    ...(options.headers || {}),
    "X-Actor-Id": actorId,
    "X-Actor-Roles": actorRoles.join(","),
  };
  const response = await fetch(url, { ...options, headers });
  // 其余逻辑不变
}
```

**所有 API 方法**中将原本 payload 里的 `actorId`、`actorRoles` 字段**从 body 移除**，改为传给 `requestJson`：

改造前：
```javascript
body: JSON.stringify({ version, actorId, actorRoles: ["INITIATOR"] })
```
改造后：
```javascript
body: JSON.stringify({ version }),
// actorId 和 actorRoles 由 requestJson 自动加到 Header
```

**GET 请求**中从 query string 移除 `actorId` 和 `actorRoles` 参数。

改造前（getAdminRegistrations）：
```javascript
`${this.baseUrl}/api/v1/admin/registrations?actorId=${encodeURIComponent(actorId)}&actorRoles=${encodeURIComponent(roles)}`
```
改造后：
```javascript
`${this.baseUrl}/api/v1/admin/registrations`
```

**app.js 中**，凡是调用 api 方法时传入 `actorId`/`actorRoles` 参数的地方，也需要对应删除（因为现在由 ApiClient 内部持有）。

涉及的 app.js 改动点（搜索关键词）：
- `api.getAdminRegistrations(actorId, actorRoles)` → `api.getAdminRegistrations()`
- `api.getAdminRegistrationDetail(registrationId, actorId, actorRoles)` → `api.getAdminRegistrationDetail(registrationId)`
- `api.updateRegistrationNotes(registrationId, { ..., actorId, actorRoles })` → payload 中移除 actorId/actorRoles
- `api.updateRegistrationStatus(registrationId, { ..., actorId, actorRoles })` → 同上

**同时**，`app.js` 中角色切换后需刷新 api 实例的 actor 信息：
```javascript
function toggleAdminMode() {
  // ... 现有逻辑
  api.refreshActor(); // 新增这一行
}
```

### 自测命令

```bash
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js
```

浏览器验证（需后端已启动）：
1. 切换为管理员模式
2. 打开后台课程列表，确认数据正常加载
3. 打开 Network 面板，确认请求头含 `X-Actor-Id` 和 `X-Actor-Roles`
4. 提交一条报名，确认成功

### 验收标准
1. `node --check` 两个文件均通过
2. 所有 API 请求 Header 含 `X-Actor-Id` 和 `X-Actor-Roles`
3. 请求体中不含 `actorId` 和 `actorRoles` 字段
4. GET 请求 URL 不含 `actorId` 和 `actorRoles` 参数
5. Mock 模式下所有功能正常（不依赖后端）
6. 真实后端模式下完整业务链路通过（创建→审核→报名→管理）

---

## M7：Docker + 启动脚本更新

**任务编号**：M7  
**修改文件**：`docker/backend.Dockerfile`、`scripts/start-local.sh`、`scripts/start-local.ps1`、`scripts/stop-local.sh`、`scripts/stop-local.ps1`  
**前置依赖**：M5

### backend.Dockerfile 改造

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装生产依赖（不含 dev）
RUN uv sync --frozen --no-dev

# 复制应用代码
COPY apps /app/apps

ENV PYTHONPATH=/app
ENV GROUP_CLASS_BACKEND_HOST=0.0.0.0
ENV GROUP_CLASS_BACKEND_PORT=18000

EXPOSE 18000

CMD ["uv", "run", "uvicorn", "apps.group_class_backend.app:app", \
     "--host", "0.0.0.0", "--port", "18000"]
```

### start-local.sh 改造

将：
```bash
"${PYTHON_BIN}" -m apps.group_class_backend.server > ...
```
改为：
```bash
uv run uvicorn apps.group_class_backend.app:app \
  --host "${GROUP_CLASS_BACKEND_HOST:-0.0.0.0}" \
  --port "${BACKEND_PORT}" > /tmp/group_class_backend.log 2>&1 &
```

同步更新 `.ps1` 版本。

### 自测命令

```bash
# Linux/macOS
chmod +x scripts/start-local.sh && ./scripts/start-local.sh
curl http://127.0.0.1:18000/health
curl http://127.0.0.1:18000/api/v1/public/classes
./scripts/stop-local.sh

# Docker
docker compose up -d --build
curl http://127.0.0.1:18000/health
docker compose down
```

### 验收标准
1. `./scripts/start-local.sh` 启动成功，两个服务均可访问
2. `docker compose up --build` 成功，`/health` 返回 ok
3. 启动脚本无 `server.py` 相关字样

---

## M8：新增 API 集成测试

**任务编号**：M8  
**修改文件**：`tests/test_api/` 目录（全部新建）  
**前置依赖**：M5

### 目录结构

```
tests/
  test_api/
    __init__.py
    conftest.py          # TestClient fixture
    test_classes_api.py  # classes 路由集成测试
    test_registrations_api.py  # registrations 路由集成测试
```

### conftest.py

```python
import pytest
from fastapi.testclient import TestClient
from apps.group_class_backend.app import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_headers() -> dict:
    return {"X-Actor-Id": "u_test_admin", "X-Actor-Roles": "CLASS_ADMIN"}


@pytest.fixture
def initiator_headers() -> dict:
    return {"X-Actor-Id": "u_test_initiator", "X-Actor-Roles": "INITIATOR"}
```

### test_classes_api.py（关键测试用例）

```python
def test_public_list_classes_returns_200(client):
    resp = client.get("/api/v1/public/classes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "OK"
    assert isinstance(data["data"]["items"], list)


def test_public_list_excludes_draft(client):
    resp = client.get("/api/v1/public/classes")
    items = resp.json()["data"]["items"]
    statuses = {item["status"] for item in items}
    assert "DRAFT" not in statuses


def test_admin_list_includes_draft(client, admin_headers):
    resp = client.get("/api/v1/admin/classes", headers=admin_headers)
    items = resp.json()["data"]["items"]
    statuses = {item["status"] for item in items}
    assert "DRAFT" in statuses


def test_create_class_returns_draft(client, admin_headers):
    resp = client.post("/api/v1/admin/classes",
        json={"className": "API测试班", "classType": "GROUP_CLASS", "minStudents": 4},
        headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "DRAFT"


def test_create_class_missing_name_returns_400(client, admin_headers):
    resp = client.post("/api/v1/admin/classes",
        json={"classType": "GROUP_CLASS"},
        headers=admin_headers)
    assert resp.status_code == 400


def test_full_review_workflow(client, initiator_headers, admin_headers):
    # 创建
    resp = client.post("/api/v1/admin/classes",
        json={"className": "审核流测试", "minStudents": 3},
        headers=initiator_headers)
    class_id = resp.json()["data"]["classId"]
    version = resp.json()["data"]["version"]

    # 提交审核
    resp = client.post(f"/api/v1/admin/classes/{class_id}/submit-review",
        json={"version": version}, headers=initiator_headers)
    assert resp.json()["data"]["status"] == "PENDING_REVIEW"
    version = resp.json()["data"]["version"]

    # 审核通过
    resp = client.post(f"/api/v1/admin/classes/{class_id}/approve",
        json={"version": version}, headers=admin_headers)
    assert resp.json()["data"]["status"] == "OPEN_FOR_ENROLLMENT"


def test_approve_without_admin_role_returns_403(client, initiator_headers):
    # 先创建并提交审核
    resp = client.post("/api/v1/admin/classes",
        json={"className": "权限测试", "minStudents": 3},
        headers=initiator_headers)
    class_id = resp.json()["data"]["classId"]
    version = resp.json()["data"]["version"]
    client.post(f"/api/v1/admin/classes/{class_id}/submit-review",
        json={"version": version}, headers=initiator_headers)

    # 用 INITIATOR 角色审核，应 403
    resp = client.post(f"/api/v1/admin/classes/{class_id}/approve",
        json={"version": version + 1}, headers=initiator_headers)
    assert resp.status_code == 403


def test_version_conflict_returns_409(client, admin_headers):
    resp = client.post("/api/v1/admin/classes",
        json={"className": "版本冲突测试", "minStudents": 3},
        headers=admin_headers)
    class_id = resp.json()["data"]["classId"]
    # 传错误的 version
    resp = client.post(f"/api/v1/admin/classes/{class_id}/update",
        json={"version": 999, "className": "新名称"},
        headers=admin_headers)
    assert resp.status_code == 409
```

### test_registrations_api.py（关键测试用例，Codex 按模式补齐）

```python
def test_submit_registration_success(client, admin_headers):
    # 创建并审核通过一个课程
    ...
    # 提交报名
    resp = client.post("/api/v1/public/registrations",
        json={"classId": class_id, "registerType": "ENROLLMENT",
              "parentName": "张三", "contactInfo": "13800138000",
              "studentName": "小明", "studentGrade": "三年级"},
        headers={"X-Actor-Id": "u_parent_001"})
    assert resp.status_code == 200
    assert resp.json()["data"]["registrationId"].startswith("reg-")


def test_list_registrations_requires_role(client):
    resp = client.get("/api/v1/admin/registrations",
        headers={"X-Actor-Id": "u_nobody"})
    assert resp.status_code == 403
```

### 自测命令

```bash
uv run pytest tests/ -q
# 期望：全部通过（原有 91 个 + 新增 ≥ 15 个）
```

### 验收标准
1. 新增测试用例 ≥ 15 个
2. 所有测试（含原有 91 个）全部通过
3. 覆盖：只读路由、写操作、审核流、权限拒绝、version 冲突、报名提交、报名管理

---

## M9：server.py 删除 + 文档更新

**任务编号**：M9  
**修改文件**：`apps/group_class_backend/server.py`（删除）、`CLAUDE.md`（更新）、`README.md`（更新）  
**前置依赖**：M8（所有测试通过）

### 执行步骤

1. 确认 `uv run pytest tests/ -q` 全部通过
2. 确认端到端 curl 链路通过（参考 M4/M5 自测命令）
3. `git rm apps/group_class_backend/server.py`
4. 更新 `CLAUDE.md` 中的启动命令和架构描述
5. 更新 `README.md` 中的启动命令

### CLAUDE.md 更新内容

启动命令改为：
```bash
# 后端
uv run uvicorn apps.group_class_backend.app:app --host 0.0.0.0 --port 18000 --reload

# 测试
uv run pytest tests/ -q

# 单个测试文件
uv run pytest tests/group_class_backend/classes/test_create_class_draft.py -q

# 前端语法检查
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js
```

架构描述更新：
- HTTP 层由 FastAPI + uvicorn 提供
- 身份信息通过 `X-Actor-Id` / `X-Actor-Roles` Header 传递
- `apps/group_class_backend/deps.py` 封装 `ActorContext` 依赖注入，后期替换为 JWT 只改此文件
- `apps/group_class_backend/routers/` 包含两个路由文件（classes、registrations）

### 验收标准
1. `server.py` 不存在
2. `uv run pytest tests/ -q` 全部通过
3. CLAUDE.md 启动命令可直接复制执行
4. README.md 无 `server.py` 相关字样

---

## 进度跟踪表（Codex 每完成一项更新此表）

| 编号 | 任务名称 | 状态 | 完成时间 | 自测结果 | 备注 |
|---|---|---|---|---|---|
| M1 | uv 项目初始化 | 待开始 | - | - | - |
| M2 | FastAPI 骨架 + deps | 待开始 | - | - | - |
| M3 | classes 只读路由 | 待开始 | - | - | - |
| M4 | classes 写操作 + 审核 | 待开始 | - | - | - |
| M5 | registrations 路由 | 待开始 | - | - | - |
| M6 | 前端 Header 改造 | 待开始 | - | - | - |
| M7 | Docker + 脚本更新 | 待开始 | - | - | - |
| M8 | API 集成测试 | 待开始 | - | - | - |
| M9 | server.py 删除 + 文档 | 待开始 | - | - | - |

---

## 全量验收检查单（M9 完成后执行）

```bash
# 1. 单元 + 集成测试
uv run pytest tests/ -q
# 期望：≥ 106 passed（原 91 + 新增 ≥ 15）

# 2. 前端语法
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js

# 3. 端到端业务链路（启动后端后执行）
uv run uvicorn apps.group_class_backend.app:app --host 127.0.0.1 --port 18000

## 3.1 创建课程
CLASS_ID=$(curl -s -X POST http://127.0.0.1:18000/api/v1/admin/classes \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_test" -H "X-Actor-Roles: INITIATOR" \
  -d '{"className":"验收测试班","minStudents":3}' | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['classId'])")
echo "classId: $CLASS_ID"

## 3.2 提交审核
curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID/submit-review" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_test" -H "X-Actor-Roles: INITIATOR" \
  -d '{"version":1}' | python3 -c "import sys,json;d=json.load(sys.stdin);print('status:',d['data']['status'])"

## 3.3 审核通过
curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID/approve" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_admin" -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"version":2}' | python3 -c "import sys,json;d=json.load(sys.stdin);print('status:',d['data']['status'])"

## 3.4 前台可见
curl -s http://127.0.0.1:18000/api/v1/public/classes | python3 -c "import sys,json;d=json.load(sys.stdin);print('total:',d['data']['total'])"

## 3.5 提交报名
REG_ID=$(curl -s -X POST http://127.0.0.1:18000/api/v1/public/registrations \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_parent" \
  -d "{\"classId\":\"$CLASS_ID\",\"registerType\":\"ENROLLMENT\",\"parentName\":\"张三\",\"contactInfo\":\"13800138000\",\"studentName\":\"小明\",\"studentGrade\":\"三年级\"}" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['registrationId'])")
echo "registrationId: $REG_ID"

## 3.6 后台查看报名
curl -s "http://127.0.0.1:18000/api/v1/admin/registrations" \
  -H "X-Actor-Id: u_admin" -H "X-Actor-Roles: CLASS_ADMIN" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print('items:',len(d['data']['items']))"

## 3.7 server.py 不存在
ls apps/group_class_backend/server.py 2>&1 | grep "No such file"
```

**通过标准**：所有命令输出符合预期，`server.py` 不存在，测试全部通过。

---

## Claude Review 清单（每个 M 任务完成后执行）

### M1-M2 Review
- [ ] pyproject.toml 依赖版本合理，无多余依赖
- [ ] `uv.lock` 已提交
- [ ] lifespan 正确初始化 AppState
- [ ] `_seed_classes` 完整复制，三个种子数据均存在

### M3-M4 Review
- [ ] 所有 14 条路由 HTTP 状态码与旧 server.py 完全一致
- [ ] controller 调用参数无遗漏
- [ ] 没有在路由层做业务逻辑
- [ ] 91 个原有测试仍全部通过

### M5 Review
- [ ] registrations 5 条路由全部接入
- [ ] submit_registration 的 actor_id 来自 Header，不从 body 读

### M6 Review
- [ ] 所有 requestJson 调用均传递 actor Header
- [ ] body 中无 actorId/actorRoles 字段残留
- [ ] GET URL 中无 actorId/actorRoles 参数残留
- [ ] mock 模式下无报错

### M7 Review
- [ ] Dockerfile 使用 uv，无 pip 命令
- [ ] 脚本中无 server.py 字样
- [ ] docker compose 构建成功

### M8 Review
- [ ] 新增测试 ≥ 15 个
- [ ] 覆盖正向 + 负向（权限、version 冲突、参数校验）
- [ ] 使用 fixture，无重复代码

### M9 Review
- [ ] server.py 已删除
- [ ] CLAUDE.md 启动命令已更新
- [ ] 无遗留 TODO 或 FIXME
