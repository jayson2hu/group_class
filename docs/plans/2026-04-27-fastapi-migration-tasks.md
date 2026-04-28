# FastAPI 迁移任务书

Date: 2026-04-27  
Status: Ready for Codex Execution  
Owner: Jayson  
Final Review: Claude  

---

## 阅读本文档的方式

- **Codex** 按编号顺序逐个任务执行，每个任务完成后必须自测并填写「进度记录」，验收通过才算交付
- **Claude** 在 Codex 声明全部任务完成后，执行「Claude 总体验收清单」
- 文档顶部进度表由 Codex 实时维护，每完成一个任务立即更新状态

---

## 进度总览（Codex 实时更新）

| 编号 | 任务名称 | 状态 | 自测通过 | 完成时间 |
|---|---|---|---|---|
| M1 | uv 初始化 | ✅ 自测通过 | 通过 | 2026-04-28 07:58 CST |
| M2-A | deps.py ActorContext | ✅ 自测通过 | 通过 | 2026-04-28 08:00 CST |
| M2-B | app.py 骨架 + 种子数据 | ✅ 自测通过 | 通过 | 2026-04-28 17:43 CST |
| M2-C | routers 目录初始化 | ✅ 自测通过 | 通过 | 2026-04-28 17:44 CST |
| M3-A | 前台 classes 只读路由 | ✅ 自测通过 | 通过 | 2026-04-28 17:48 CST |
| M3-B | 后台 classes 只读路由 | ✅ 自测通过 | 通过 | 2026-04-28 17:49 CST |
| M4-A | 课程创建路由 | ✅ 自测通过 | 通过 | 2026-04-28 17:50 CST |
| M4-B | 课程更新路由 | ✅ 自测通过 | 通过 | 2026-04-28 17:51 CST |
| M4-C | 审核流三条路由 | ✅ 自测通过 | 通过 | 2026-04-28 17:53 CST |
| M5-A | 前台报名提交路由 | ✅ 自测通过 | 通过 | 2026-04-28 17:56 CST |
| M5-B | 后台报名读路由 | ✅ 自测通过 | 通过 | 2026-04-28 17:57 CST |
| M5-C | 后台报名写路由 | ✅ 自测通过 | 通过 | 2026-04-28 17:58 CST |
| M6-A | api.js requestJson Header 注入 | ✅ 自测通过 | 通过 | 2026-04-28 18:01 CST |
| M6-B | api.js 各方法清理 actorId | ✅ 自测通过 | 通过 | 2026-04-28 18:01 CST |
| M6-C | app.js 联动更新 | ✅ 自测通过 | 通过 | 2026-04-28 18:02 CST |
| M7-A | backend.Dockerfile 更新 | ❌ 自测失败 | Docker daemon 未运行 | 2026-04-28 18:05 CST |
| M7-B | 启动脚本更新 | ❌ 自测失败 | 当前执行环境清理后台进程 | 2026-04-28 18:07 CST |
| M8-A | TestClient conftest | ✅ 自测通过 | 通过 | 2026-04-28 18:11 CST |
| M8-B | classes API 集成测试 | ✅ 自测通过 | 15 passed | 2026-04-28 18:11 CST |
| M8-C | registrations API 集成测试 | ✅ 自测通过 | 13 passed | 2026-04-28 18:11 CST |
| M9 | server.py 删除 + 文档同步 | ✅ 自测通过 | 通过 | 2026-04-28 18:16 CST |

状态说明：⬜ 待开始 / 🔄 进行中 / ✅ 自测通过 / ❌ 自测失败

---

## 全局开发规范

### 文件结构（完成后）

```
group_class/
├── pyproject.toml          ← M1 新建
├── uv.lock                 ← M1 生成
├── .python-version         ← M1 新建
├── apps/group_class_backend/
│   ├── app.py              ← M2-B 新建（替代 server.py）
│   ├── deps.py             ← M2-A 新建
│   ├── routers/
│   │   ├── __init__.py     ← M3-A 新建
│   │   ├── classes.py      ← M3/M4 新建
│   │   └── registrations.py← M5 新建
│   ├── server.py           ← M9 删除
│   └── [其他目录不动]
├── tests/
│   ├── group_class_backend/ ← 现有后端测试不改（当前预期约 91 个 pytest case）
│   └── test_api/           ← M8 新建
│       ├── conftest.py
│       ├── test_classes_api.py
│       └── test_registrations_api.py
```

### 代码规范

1. 所有 `.py` 文件首行：`from __future__ import annotations`
2. 路由函数用 **同步** `def`，不用 `async def`（controller 全是同步的）
3. 路由层职责：参数解析 → 调用 controller → 映射 HTTP 状态码 → 返回 result dict
4. **禁止**在路由层写业务逻辑
5. HTTP 状态码映射统一用辅助函数 `_http_status(result)`
6. `actorId` / `actorRoles` **只从 Header 读**，不从 body 或 query string 读
7. 路由层必须将 `actor.actor_roles` 原样传给 controller，空角色传 `[]`，不要把空列表转换成 `None`

### actorId 传递协议

| 场景 | Header 名 | 默认值 |
|---|---|---|
| 发起人 ID | `X-Actor-Id` | `u_anonymous` |
| 角色列表 | `X-Actor-Roles` | `""` (空) |

前端所有请求统一在 Header 注入，body 和 query string 中**不再包含** actorId/actorRoles。

权限语义：

- `X-Actor-Roles` 为空表示无角色，后端应按无权限处理需要角色的操作
- 不再保留旧 `server.py` 中 `actor_roles=None` 的宽松兼容行为
- 路由层禁止使用 `actor.actor_roles if actor.actor_roles else None`

### commit 规范

如果用户明确授权提交代码，每个子任务完成后单独 commit；若用户未授权，则只更新文件和进度记录，不主动提交：
```
feat(M1): uv 项目初始化，新增 pyproject.toml 和 .python-version
feat(M2-A): 新增 deps.py，ActorContext 依赖注入
feat(M2-B): 新增 app.py，FastAPI 骨架与种子数据
...
```

### 自测规范

- 每个子任务有专属「自测命令」，**必须全部执行并截图/粘贴输出**
- 发现失败必须修复后重新自测，不允许带失败项交付
- 自测输出格式：在进度记录中写 `自测通过：<关键输出摘要>`

---

## M1：uv 项目初始化

**前置依赖**：无  
**修改文件**：`pyproject.toml`（新建）、`.python-version`（新建）、`.gitignore`（追加）

### 实现内容

**pyproject.toml**（项目根目录）：

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

**.python-version**：
```
3.12
```

**.gitignore** 末尾追加（若 `.venv/` 已存在则跳过）：
```
.venv/
```

### 自测命令

```bash
cd /path/to/group_class

# 安装 uv（若未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依赖
uv sync --dev

# 验证
uv run python --version
uv run python -c "import fastapi; print('fastapi', fastapi.__version__)"
uv run python -c "import uvicorn; print('uvicorn', uvicorn.__version__)"
uv run python -c "import httpx; print('httpx', httpx.__version__)"
uv run python -c "import pytest; print('pytest', pytest.__version__)"
```

### 验收标准（Codex 自测全部通过才交付）

- [ ] `uv sync --dev` 无报错
- [ ] `uv.lock` 文件已生成
- [ ] `python --version` 输出 3.12.x
- [ ] fastapi、uvicorn、httpx、pytest 均可正常 import
- [ ] `.venv/` 在 `.gitignore` 中（不提交到 git）
- [ ] `uv.lock` 提交到 git

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- `uv sync --dev` 通过，生成 `uv.lock` 和 `.venv/`
- `uv run python --version` -> `Python 3.12.2`
- fastapi 0.136.1 / uvicorn 0.46.0 / httpx 0.28.1 / pytest 9.0.3 均可 import
- `.gitignore` 已包含 `.venv/`
完成时间：2026-04-28 07:58 CST
```

---

## M2-A：deps.py ActorContext 依赖注入

**前置依赖**：M1  
**修改文件**：`apps/group_class_backend/deps.py`（新建）

### 实现内容

```python
from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import Header


@dataclass(frozen=True)
class ActorContext:
    """请求发起人身份上下文，由 FastAPI Depends 注入路由函数。"""
    actor_id: str
    actor_roles: list[str] = field(default_factory=list)


def get_actor(
    x_actor_id: str = Header(default="u_anonymous"),
    x_actor_roles: str = Header(default=""),
) -> ActorContext:
    """从 HTTP Header 解析 actor 信息。后期替换为 JWT 只改此函数。"""
    roles = [r.strip() for r in x_actor_roles.split(",") if r.strip()]
    return ActorContext(actor_id=x_actor_id, actor_roles=roles)
```

### 自测命令

```bash
# 语法检查
uv run python -c "from apps.group_class_backend.deps import get_actor, ActorContext; print('deps OK')"

# 逻辑验证
uv run python -c "
from apps.group_class_backend.deps import ActorContext
ctx = ActorContext(actor_id='u_test', actor_roles=['CLASS_ADMIN', 'INITIATOR'])
assert ctx.actor_id == 'u_test'
assert 'CLASS_ADMIN' in ctx.actor_roles
print('ActorContext OK')
"
```

### 验收标准

- [ ] `from apps.group_class_backend.deps import get_actor, ActorContext` 无报错
- [ ] `ActorContext` 是 frozen dataclass（不可变）
- [ ] `get_actor` 函数签名正确，使用 `Header(default=...)`
- [ ] 空 `X-Actor-Roles` header 时 `actor_roles` 为空列表 `[]`
- [ ] 逗号分隔的角色被正确解析为列表

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- `from apps.group_class_backend.deps import get_actor, ActorContext` -> `deps OK`
- `ActorContext(actor_id='u_test', actor_roles=['CLASS_ADMIN', 'INITIATOR'])` 断言通过
- `get_actor('u1', '')` 返回空角色列表，逗号分隔角色解析通过
完成时间：2026-04-28 08:00 CST
```

---

## M2-B：app.py 骨架 + 种子数据

**前置依赖**：M2-A  
**修改文件**：`apps/group_class_backend/app.py`（新建）

### 实现内容

```python
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

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


_state: AppState | None = None


def get_state() -> AppState:
    assert _state is not None, "AppState not initialized"
    return _state


def new_request_id() -> str:
    return f"req-{uuid4().hex[:12]}"


def _seed_classes(repo: InMemoryClassRepository) -> None:
    """
    与 server.py 保持完全一致的种子数据。
    Codex: 请完整复制 server.py 第 37-110 行的三个种子课程实现。
    不要省略任何一个课程，不要更改字段值。
    """
    # TODO: Codex 在此处复制 server.py 的 _seed_classes 完整实现
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _state
    _state = AppState()
    yield
    _state = None


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


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}
```

**重要**：`_seed_classes` 函数必须完整复制 `server.py` 第 37-110 行的内容，包含三个种子课程（三年级英语拼课班、四年级阅读强化班、后台草稿示例班），字段值不得更改。

### 自测命令

```bash
# 启动应用（保持运行，另开终端执行后续命令）
uv run uvicorn apps.group_class_backend.app:app --host 127.0.0.1 --port 18000

# 另一个终端
curl -s http://127.0.0.1:18000/health
# 期望输出：{"status":"ok","version":"0.1.0"}

curl -i -s -H "Origin: http://127.0.0.1:5173" http://127.0.0.1:18000/health
# 期望：响应头含 access-control-allow-origin: *

# 访问 Swagger
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18000/docs
# 期望：200

# 验证种子数据已加载（路由 M3 后才能访问，此处验证 AppState 初始化）
uv run python -c "
from apps.group_class_backend.app import AppState
s = AppState()
classes = s.class_repository.list()
print('seed count:', len(classes))
assert len(classes) == 3, f'期望3个种子课程，实际{len(classes)}'
statuses = {c.status.value for c in classes}
print('statuses:', statuses)
assert 'OPEN_FOR_ENROLLMENT' in statuses
assert 'FULL' in statuses
assert 'DRAFT' in statuses
print('seed data OK')
"
```

### 验收标准

- [ ] 应用启动无报错
- [ ] `GET /health` 返回 `{"status":"ok","version":"0.1.0"}`
- [ ] CORS 头 `access-control-allow-origin: *` 存在
- [ ] `GET /docs` 返回 200（Swagger UI）
- [ ] 种子数据正确：3 个课程，包含 OPEN_FOR_ENROLLMENT、FULL、DRAFT 各一个
- [ ] `lifespan` 正确使用，`_state` 在 yield 后设为 None

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出（health 响应 + seed count）：
- `GET /health` -> `{"status":"ok","version":"0.1.0"}`
- 带 `Origin` 的 `GET /health` 响应头含 `access-control-allow-origin: *`
- `GET /docs` -> `200`
- AppState 种子数据：`seed count: 3`，状态含 `OPEN_FOR_ENROLLMENT` / `FULL` / `DRAFT`
完成时间：2026-04-28 17:43 CST
```

---

## M2-C：routers 目录初始化

**前置依赖**：M2-B  
**修改文件**：`apps/group_class_backend/routers/__init__.py`（新建空文件）

### 实现内容

创建目录和空 `__init__.py`：

```bash
mkdir -p apps/group_class_backend/routers
touch apps/group_class_backend/routers/__init__.py
```

### 自测命令

```bash
uv run python -c "from apps.group_class_backend import routers; print('routers package OK')"
ls apps/group_class_backend/routers/
# 期望：__init__.py
```

### 验收标准

- [ ] `apps/group_class_backend/routers/__init__.py` 存在
- [ ] `from apps.group_class_backend import routers` 无报错

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- `from apps.group_class_backend import routers` -> `routers package OK`
- `ls apps/group_class_backend/routers/` -> `__init__.py`
完成时间：2026-04-28 17:44 CST
```

---

## M3-A：前台 classes 只读路由

**前置依赖**：M2-C  
**修改文件**：`apps/group_class_backend/routers/classes.py`（新建）、`apps/group_class_backend/app.py`（注册路由）

### 接口

| 方法 | 路径 | controller | 说明 |
|---|---|---|---|
| GET | `/api/v1/public/classes` | `list_classes(public_only=True)` | 前台看板，只含公开状态 |
| GET | `/api/v1/public/classes/{class_id}` | `get_class_detail(public_only=True)` | 前台详情 |

### 实现要点

```python
# apps/group_class_backend/routers/classes.py
from __future__ import annotations

from fastapi import APIRouter, Response

from apps.group_class_backend.app import get_state, new_request_id
from apps.group_class_backend.classes.controller import get_class_detail, list_classes
from apps.group_class_backend.common.error_codes import ErrorCode

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
def public_list_classes(
    page: int = 1,
    page_size: int = 20,
    response: Response = None,
):
    state = get_state()
    result = list_classes(
        repository=state.class_repository,
        request_id=new_request_id(),
        page=page,
        page_size=min(page_size, 100),
        public_only=True,
    )
    response.status_code = _http_status(result)
    return result


@router.get("/api/v1/public/classes/{class_id}")
def public_get_class_detail(class_id: str, response: Response = None):
    state = get_state()
    result = get_class_detail(
        class_id=class_id,
        repository=state.class_repository,
        request_id=new_request_id(),
        public_only=True,
    )
    response.status_code = _http_status(result)
    return result
```

在 `app.py` 中注册路由（在 health 路由之前）：

```python
from apps.group_class_backend.routers import classes as classes_router
app.include_router(classes_router.router)
```

### 自测命令

```bash
uv run uvicorn apps.group_class_backend.app:app --host 127.0.0.1 --port 18000

# 前台列表
curl -s http://127.0.0.1:18000/api/v1/public/classes | python3 -m json.tool
# 期望：code=OK，data.items 含 2 条（OPEN_FOR_ENROLLMENT + FULL）

# 验证 DRAFT 不在前台列表
curl -s http://127.0.0.1:18000/api/v1/public/classes | python3 -c "
import sys, json
d = json.load(sys.stdin)
statuses = {i['status'] for i in d['data']['items']}
print('statuses:', statuses)
assert 'DRAFT' not in statuses, 'DRAFT 不应出现在前台列表'
print('PASS: DRAFT 已过滤')
"

# 前台详情（用列表中返回的 classId）
CLASS_ID=$(curl -s http://127.0.0.1:18000/api/v1/public/classes | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['items'][0]['classId'])")
curl -s "http://127.0.0.1:18000/api/v1/public/classes/$CLASS_ID" | python3 -m json.tool
# 期望：code=OK，data.classId = CLASS_ID

# 不存在的课程
curl -s -w "\nHTTP:%{http_code}" "http://127.0.0.1:18000/api/v1/public/classes/cls-notexist"
# 期望：HTTP:404

# 分页
curl -s "http://127.0.0.1:18000/api/v1/public/classes?page=1&page_size=1" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert len(d['data']['items']) == 1, '分页应只返回1条'
print('PASS: 分页正常')
"

# 响应格式验证
curl -s http://127.0.0.1:18000/api/v1/public/classes | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert 'requestId' in d
assert 'code' in d
assert 'data' in d
assert 'page' in d['data']
assert 'total' in d['data']
assert 'items' in d['data']
print('PASS: 响应格式正确')
"
```

### 验收标准

- [ ] `GET /api/v1/public/classes` 返回 200，含 requestId/code/data 三个字段
- [ ] items 中不含 DRAFT 课程
- [ ] items 含种子数据中的 OPEN_FOR_ENROLLMENT 和 FULL 课程
- [ ] 分页参数 `page`/`page_size` 生效
- [ ] `page_size` 超过 100 时后端截断为 100
- [ ] 不存在的 class_id 返回 404
- [ ] DRAFT 课程的 class_id 访问前台详情返回 404

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- 前台列表 `code=OK`，公开状态为 `FULL` / `OPEN_FOR_ENROLLMENT`，不含 `DRAFT`
- 前台详情返回 `code=OK`
- 不存在课程返回 `404`
- `page_size=1` 分页生效
- DRAFT 课程前台详情返回 `404`
完成时间：2026-04-28 17:48 CST
```

---

## M3-B：后台 classes 只读路由

**前置依赖**：M3-A  
**修改文件**：`apps/group_class_backend/routers/classes.py`（追加）

### 接口

| 方法 | 路径 | controller | 说明 |
|---|---|---|---|
| GET | `/api/v1/admin/classes` | `list_classes(public_only=False)` | 后台列表，含所有状态 |
| GET | `/api/v1/admin/classes/{class_id}` | `get_class_detail(public_only=False)` | 后台详情 |

### 实现要点

与 M3-A 类似，`public_only=False`，无需 actor 参数（只读不校验权限）。

### 自测命令

```bash
# 后台列表（含 DRAFT）
curl -s http://127.0.0.1:18000/api/v1/admin/classes | python3 -c "
import sys, json
d = json.load(sys.stdin)
statuses = {i['status'] for i in d['data']['items']}
print('statuses:', statuses)
assert 'DRAFT' in statuses, 'DRAFT 应出现在后台列表'
assert len(d['data']['items']) == 3, f'期望3条，实际{len(d[\"data\"][\"items\"])}'
print('PASS: 后台列表含所有状态')
"

# 后台详情（取 DRAFT 课程）
DRAFT_ID=$(curl -s http://127.0.0.1:18000/api/v1/admin/classes | python3 -c "
import sys, json
items = json.load(sys.stdin)['data']['items']
draft = next(i for i in items if i['status'] == 'DRAFT')
print(draft['classId'])
")
curl -s "http://127.0.0.1:18000/api/v1/admin/classes/$DRAFT_ID" | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['code'] == 'OK'
assert d['data']['status'] == 'DRAFT'
print('PASS: 后台可查看 DRAFT')
"

# 不存在的课程
curl -s -w "\nHTTP:%{http_code}" "http://127.0.0.1:18000/api/v1/admin/classes/cls-notexist"
# 期望：HTTP:404
```

### 验收标准

- [ ] `GET /api/v1/admin/classes` 返回所有状态课程，含 DRAFT
- [ ] 后台详情可查看 DRAFT 课程
- [ ] 不存在的课程返回 404
- [ ] 响应格式与 M3-A 一致

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- 后台列表状态含 `DRAFT` / `FULL` / `OPEN_FOR_ENROLLMENT`，total=3
- 后台 DRAFT 详情返回 `code=OK`
- 不存在课程返回 `404`
完成时间：2026-04-28 17:49 CST
```

---

## M4-A：课程创建路由

**前置依赖**：M3-B  
**修改文件**：`apps/group_class_backend/routers/classes.py`（追加）

### 接口

| 方法 | 路径 | controller | actorId 来源 |
|---|---|---|---|
| POST | `/api/v1/admin/classes` | `create_class_draft` | Header `X-Actor-Id` |

### 实现要点

```python
from typing import Any
from fastapi import Body, Depends
from apps.group_class_backend.deps import ActorContext, get_actor
from apps.group_class_backend.classes.controller import create_class_draft
from datetime import datetime, timezone

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
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result
```

### 自测命令

```bash
# 创建成功
curl -s -X POST http://127.0.0.1:18000/api/v1/admin/classes \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_test" \
  -H "X-Actor-Roles: INITIATOR" \
  -d '{"className":"测试创建班","classType":"GROUP_CLASS","minStudents":4,"maxStudents":8}' \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['code'] == 'OK', f'期望OK，实际{d}'
assert d['data']['status'] == 'DRAFT'
assert d['data']['classId'].startswith('cls-')
assert d['data']['version'] == 1
assert d['data']['creatorId'] == 'u_test'
print('PASS: 创建课程成功，classId:', d['data']['classId'])
"

# 缺少 className 和 templateId（必须报错）
curl -s -w "\nHTTP:%{http_code}" -X POST http://127.0.0.1:18000/api/v1/admin/classes \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_test" \
  -d '{"classType":"GROUP_CLASS"}'
# 期望：HTTP:400，code=VALIDATION_INVALID_ARGUMENT

# 验证 creatorId 来自 Header 而非 body
curl -s -X POST http://127.0.0.1:18000/api/v1/admin/classes \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_header_user" \
  -d '{"className":"Header测试","minStudents":3}' \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['data']['creatorId'] == 'u_header_user', f'creatorId应来自Header，实际{d[\"data\"][\"creatorId\"]}'
print('PASS: creatorId 正确来自 Header')
"

# 验证后台列表数量增加
BEFORE=$(curl -s http://127.0.0.1:18000/api/v1/admin/classes | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['total'])")
curl -s -X POST http://127.0.0.1:18000/api/v1/admin/classes \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_test" \
  -d '{"className":"计数测试班","minStudents":3}' > /dev/null
AFTER=$(curl -s http://127.0.0.1:18000/api/v1/admin/classes | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['total'])")
python3 -c "assert $AFTER == $BEFORE + 1, f'期望{$BEFORE+1}，实际{$AFTER}'; print('PASS: 列表数量正确增加')"
```

### 验收标准

- [ ] 创建成功返回 200，status=DRAFT，version=1
- [ ] `classId` 以 `cls-` 开头
- [ ] `creatorId` 来自 `X-Actor-Id` Header，不从 body 读
- [ ] 缺少 className 且无 templateId 返回 400，code=VALIDATION_INVALID_ARGUMENT
- [ ] 创建后后台列表数量 +1

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- 创建课程成功，返回 `DRAFT`、`version=1`、`classId` 以 `cls-` 开头
- 缺少 `className/templateId` 返回 `400`，code=`VALIDATION_INVALID_ARGUMENT`
- `creatorId` 正确来自 `X-Actor-Id`
- 创建后后台列表 total 从 5 增至 6
完成时间：2026-04-28 17:50 CST
```

---

## M4-B：课程更新路由

**前置依赖**：M4-A  
**修改文件**：`apps/group_class_backend/routers/classes.py`（追加）

### 接口

| 方法 | 路径 | controller | 说明 |
|---|---|---|---|
| POST | `/api/v1/admin/classes/{class_id}/update` | `update_class_draft` | 需要 version 字段 |

### 自测命令

```bash
# 先创建一个课程
CLASS_JSON=$(curl -s -X POST http://127.0.0.1:18000/api/v1/admin/classes \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_test" -H "X-Actor-Roles: INITIATOR" \
  -d '{"className":"更新测试","minStudents":3}')
CLASS_ID=$(echo $CLASS_JSON | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['classId'])")
VERSION=$(echo $CLASS_JSON | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['version'])")
echo "classId=$CLASS_ID version=$VERSION"

# 更新成功
curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID/update" \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_test" -H "X-Actor-Roles: INITIATOR" \
  -d "{\"version\":$VERSION,\"className\":\"更新后的名称\",\"minStudents\":5}" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['code'] == 'OK'
assert d['data']['className'] == '更新后的名称'
assert d['data']['version'] == 2
print('PASS: 更新成功，version 递增为 2')
"

# version 冲突（用旧 version）
curl -s -w "\nHTTP:%{http_code}" -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID/update" \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_test" -H "X-Actor-Roles: INITIATOR" \
  -d "{\"version\":$VERSION,\"className\":\"冲突测试\"}"
# 期望：HTTP:409，code=CLASS_VERSION_CONFLICT

# 课程不存在
curl -s -w "\nHTTP:%{http_code}" -X POST "http://127.0.0.1:18000/api/v1/admin/classes/cls-notexist/update" \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_test" -H "X-Actor-Roles: INITIATOR" \
  -d '{"version":1,"className":"不存在"}'
# 期望：HTTP:404
```

### 验收标准

- [ ] 更新成功返回 200，字段已更新，version 递增
- [ ] version 不匹配返回 409，code=CLASS_VERSION_CONFLICT
- [ ] class_id 不存在返回 404
- [ ] `actorId` 来自 Header，body 中无 actorId 字段也能正常工作
- [ ] `actorRoles` 来自 Header；空 `X-Actor-Roles` 作为空列表传入，不转换成 `None`

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- 更新成功，`className` 已变更，`version` 递增为 2
- 旧 version 更新返回 `409`，code=`CLASS_VERSION_CONFLICT`
- 不存在课程更新返回 `404`
完成时间：2026-04-28 17:51 CST
```

---

## M4-C：审核流三条路由

**前置依赖**：M4-B  
**修改文件**：`apps/group_class_backend/routers/classes.py`（追加）

### 接口

| 方法 | 路径 | controller | 角色要求 |
|---|---|---|---|
| POST | `/api/v1/admin/classes/{class_id}/submit-review` | `submit_class_review` | INITIATOR（或 CLASS_ADMIN/SUPER_ADMIN） |
| POST | `/api/v1/admin/classes/{class_id}/approve` | `approve_class_review` | CLASS_ADMIN 或 SUPER_ADMIN |
| POST | `/api/v1/admin/classes/{class_id}/reject` | `reject_class_review` | CLASS_ADMIN 或 SUPER_ADMIN |

### 实现要点

```python
from apps.group_class_backend.classes.controller import (
    submit_class_review, approve_class_review, reject_class_review
)

@router.post("/api/v1/admin/classes/{class_id}/submit-review")
def admin_submit_review(
    class_id: str,
    body: dict[str, Any] = Body(...),
    actor: ActorContext = Depends(get_actor),
    response: Response = None,
):
    state = get_state()
    result = submit_class_review(
        class_id=class_id,
        payload=body,
        repository=state.class_repository,
        audit_writer=state.audit_writer,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
        now=datetime.now(timezone.utc),
    )
    response.status_code = _http_status(result)
    return result

# approve 和 reject 同理
```

### 自测命令

```bash
# 创建课程
CLASS_JSON=$(curl -s -X POST http://127.0.0.1:18000/api/v1/admin/classes \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_initiator" -H "X-Actor-Roles: INITIATOR" \
  -d '{"className":"审核流测试","minStudents":3}')
CLASS_ID=$(echo $CLASS_JSON | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['classId'])")
echo "classId=$CLASS_ID"

# 提交审核（DRAFT → PENDING_REVIEW）
SUBMIT=$(curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID/submit-review" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_initiator" -H "X-Actor-Roles: INITIATOR" \
  -d '{"version":1}')
echo $SUBMIT | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['data']['status'] == 'PENDING_REVIEW', f'期望PENDING_REVIEW，实际{d}'
print('PASS: 提交审核成功，status=PENDING_REVIEW')
"
V2=$(echo $SUBMIT | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['version'])")

# 无管理员权限尝试审核通过（应 403）
curl -s -w "\nHTTP:%{http_code}" -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID/approve" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_initiator" -H "X-Actor-Roles: INITIATOR" \
  -d "{\"version\":$V2}"
# 期望：HTTP:403

# 审核通过（PENDING_REVIEW → OPEN_FOR_ENROLLMENT）
APPROVE=$(curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID/approve" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_admin" -H "X-Actor-Roles: CLASS_ADMIN" \
  -d "{\"version\":$V2}")
echo $APPROVE | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['data']['status'] == 'OPEN_FOR_ENROLLMENT', f'期望OPEN_FOR_ENROLLMENT，实际{d}'
assert d['data']['reviewerId'] == 'u_admin'
print('PASS: 审核通过，status=OPEN_FOR_ENROLLMENT，reviewerId=u_admin')
"

# 验证审核后前台可见
curl -s http://127.0.0.1:18000/api/v1/public/classes | python3 -c "
import sys, json
items = json.load(sys.stdin)['data']['items']
ids = [i['classId'] for i in items]
assert '$CLASS_ID' in ids, f'审核通过的课程应在前台可见'
print('PASS: 审核后前台可见')
"

# 测试驳回流程
CLASS_JSON2=$(curl -s -X POST http://127.0.0.1:18000/api/v1/admin/classes \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_initiator" -H "X-Actor-Roles: INITIATOR" \
  -d '{"className":"驳回测试","minStudents":3}')
CLASS_ID2=$(echo $CLASS_JSON2 | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['classId'])")
curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID2/submit-review" \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_initiator" -H "X-Actor-Roles: INITIATOR" -d '{"version":1}' > /dev/null
REJECT=$(curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID2/reject" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_admin" -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"version":2}')
echo $REJECT | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['data']['status'] == 'REJECTED'
print('PASS: 驳回成功，status=REJECTED')
"
```

### 验收标准

- [ ] submit-review：DRAFT → PENDING_REVIEW，200
- [ ] submit-review：无角色返回 403
- [ ] submit-review：非 DRAFT/REJECTED 状态提交返回 400
- [ ] approve：PENDING_REVIEW → OPEN_FOR_ENROLLMENT，reviewerId 正确记录
- [ ] approve：非 CLASS_ADMIN/SUPER_ADMIN 角色返回 403
- [ ] reject：PENDING_REVIEW → REJECTED，200
- [ ] reject：非 CLASS_ADMIN/SUPER_ADMIN 角色返回 403
- [ ] 审核通过后课程在前台看板可见
- [ ] 驳回后课程前台不可见

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- 无角色 submit-review 返回 `403`
- DRAFT submit-review 成功转为 `PENDING_REVIEW`
- INITIATOR approve 返回 `403`
- CLASS_ADMIN approve 成功转为 `OPEN_FOR_ENROLLMENT`，`reviewerId=u_admin`
- 审核通过后前台可见
- 非 DRAFT/REJECTED 再提交返回 `400`
- reject 成功转为 `REJECTED`，驳回后前台不可见
完成时间：2026-04-28 17:53 CST
```

---

## M5-A：前台报名提交路由

**前置依赖**：M2-C（可与 M4 并行开始）  
**修改文件**：`apps/group_class_backend/routers/registrations.py`（新建）、`app.py`（注册路由）

### 接口

| 方法 | 路径 | controller |
|---|---|---|
| POST | `/api/v1/public/registrations` | `submit_registration` |

### 实现要点

```python
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, Response

from apps.group_class_backend.app import get_state, new_request_id
from apps.group_class_backend.common.error_codes import ErrorCode
from apps.group_class_backend.deps import ActorContext, get_actor
from apps.group_class_backend.registrations.controller import submit_registration

router = APIRouter()


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
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        now=datetime.now(timezone.utc),
    )
    response.status_code = 200 if result.get("code") == ErrorCode.OK.value else 400
    return result
```

在 `app.py` 中注册：
```python
from apps.group_class_backend.routers import registrations as registrations_router
app.include_router(registrations_router.router)
```

### 自测命令

```bash
# 先获取一个 OPEN_FOR_ENROLLMENT 状态的课程 ID（种子数据中有）
CLASS_ID=$(curl -s http://127.0.0.1:18000/api/v1/public/classes | python3 -c "
import sys, json
items = json.load(sys.stdin)['data']['items']
cls = next(i for i in items if i['status'] == 'OPEN_FOR_ENROLLMENT')
print(cls['classId'])
")
echo "classId=$CLASS_ID"

# 正常报名（ENROLLMENT）
REG=$(curl -s -X POST http://127.0.0.1:18000/api/v1/public/registrations \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_parent_001" \
  -d "{\"classId\":\"$CLASS_ID\",\"registerType\":\"ENROLLMENT\",\"parentName\":\"张三\",\"contactInfo\":\"13800138000\",\"studentName\":\"小明\",\"studentGrade\":\"三年级\",\"englishLevel\":\"基础\"}")
echo $REG | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['code'] == 'OK', f'期望OK，实际{d}'
assert d['data']['registrationId'].startswith('reg-')
assert d['data']['registrationStatus'] == 'SUBMITTED'
assert d['data']['registerType'] == 'ENROLLMENT'
print('PASS: 报名成功，registrationId:', d['data']['registrationId'])
"

# 课程不存在
curl -s -w "\nHTTP:%{http_code}" -X POST http://127.0.0.1:18000/api/v1/public/registrations \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_parent" \
  -d '{"classId":"cls-notexist","registerType":"ENROLLMENT","parentName":"张三","contactInfo":"13800138000","studentName":"小明","studentGrade":"三年级"}'
# 期望：HTTP:400，code=CLASS_NOT_FOUND（实际由controller返回400）

# 缺少必填字段（parentName）
curl -s -w "\nHTTP:%{http_code}" -X POST http://127.0.0.1:18000/api/v1/public/registrations \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_parent" \
  -d "{\"classId\":\"$CLASS_ID\",\"registerType\":\"ENROLLMENT\",\"contactInfo\":\"13800138000\",\"studentName\":\"小明\",\"studentGrade\":\"三年级\"}"
# 期望：HTTP:400

# 候补报名（FULL 状态课程）
FULL_ID=$(curl -s http://127.0.0.1:18000/api/v1/public/classes | python3 -c "
import sys, json
items = json.load(sys.stdin)['data']['items']
cls = next(i for i in items if i['status'] == 'FULL')
print(cls['classId'])
")
curl -s -X POST http://127.0.0.1:18000/api/v1/public/registrations \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_parent_002" \
  -d "{\"classId\":\"$FULL_ID\",\"registerType\":\"WAITLIST\",\"parentName\":\"李四\",\"contactInfo\":\"13900139000\",\"studentGrade\":\"四年级\"}" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['code'] == 'OK'
assert d['data']['registrationStatus'] == 'WAITLISTED'
print('PASS: 候补报名成功，状态=WAITLISTED')
"
```

### 验收标准

- [ ] ENROLLMENT 报名成功，registrationId 以 reg- 开头，status=SUBMITTED
- [ ] WAITLIST 报名成功，status=WAITLISTED
- [ ] 课程不存在返回 400
- [ ] 缺少必填字段（parentName/contactInfo）返回 400
- [ ] ENROLLMENT 报名后课程 currentStudents +1（通过后台详情验证）
- [ ] WAITLIST 报名后课程 waitlistCount +1

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- ENROLLMENT 报名成功，registrationId 以 `reg-` 开头，status=`SUBMITTED`
- ENROLLMENT 后课程 `currentStudents` 从 4 增至 5
- 不存在课程返回 `400`
- 缺少 `parentName` 返回 `400`
- WAITLIST 报名成功，status=`WAITLISTED`
- WAITLIST 后课程 `waitlistCount` 从 2 增至 3
完成时间：2026-04-28 17:56 CST
```

---

## M5-B：后台报名读路由

**前置依赖**：M5-A  
**修改文件**：`apps/group_class_backend/routers/registrations.py`（追加）

### 接口

| 方法 | 路径 | controller | 权限 |
|---|---|---|---|
| GET | `/api/v1/admin/registrations` | `list_registrations` | CLASS_ADMIN/SUPER_ADMIN/INITIATOR |
| GET | `/api/v1/admin/registrations/{registration_id}` | `get_registration_detail` | 同上 |

### 实现要点

```python
from apps.group_class_backend.registrations.controller import (
    list_registrations, get_registration_detail
)

@router.get("/api/v1/admin/registrations")
def admin_list_registrations(
    actor: ActorContext = Depends(get_actor),
    response: Response = None,
):
    state = get_state()
    result = list_registrations(
        class_repository=state.class_repository,
        registration_repository=state.registration_repository,
        request_id=new_request_id(),
        actor_id=actor.actor_id,
        actor_roles=actor.actor_roles,
    )
    response.status_code = _http_status(result)
    return result
```

### 自测命令

```bash
# 先确保有报名记录（M5-A 测试后应已有）

# 有权限列表
curl -s "http://127.0.0.1:18000/api/v1/admin/registrations" \
  -H "X-Actor-Id: u_demo_creator" -H "X-Actor-Roles: CLASS_ADMIN" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['code'] == 'OK'
assert isinstance(d['data']['items'], list)
print('PASS: 报名列表，条数:', len(d['data']['items']))
"

# 无权限（无 role）
curl -s -w "\nHTTP:%{http_code}" "http://127.0.0.1:18000/api/v1/admin/registrations" \
  -H "X-Actor-Id: u_nobody"
# 期望：HTTP:403

# 报名详情
REG_ID=$(curl -s "http://127.0.0.1:18000/api/v1/admin/registrations" \
  -H "X-Actor-Id: u_demo_creator" -H "X-Actor-Roles: CLASS_ADMIN" \
  | python3 -c "import sys,json;items=json.load(sys.stdin)['data']['items'];print(items[0]['registrationId']) if items else print('')")
echo "registrationId=$REG_ID"

if [ -n "$REG_ID" ]; then
  curl -s "http://127.0.0.1:18000/api/v1/admin/registrations/$REG_ID" \
    -H "X-Actor-Id: u_demo_creator" -H "X-Actor-Roles: CLASS_ADMIN" \
    | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['code'] == 'OK'
assert 'parentName' in d['data']
assert 'contactInfo' in d['data']
print('PASS: 报名详情正确，parentName:', d['data']['parentName'])
"
fi

# 详情不存在
curl -s -w "\nHTTP:%{http_code}" "http://127.0.0.1:18000/api/v1/admin/registrations/reg-notexist" \
  -H "X-Actor-Id: u_demo_creator" -H "X-Actor-Roles: CLASS_ADMIN"
# 期望：HTTP 非200
```

### 验收标准

- [ ] 有 CLASS_ADMIN 角色可查看报名列表
- [ ] 无角色返回 403
- [ ] 报名详情含 parentName、contactInfo、studentName 等字段
- [ ] 不存在的 registrationId 返回非 200

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- CLASS_ADMIN 可查看报名列表，当前 2 条
- 无角色访问报名列表返回 `403`
- 报名详情返回 `code=OK`，含 `parentName` / `contactInfo`
- 不存在 registrationId 返回非 200（实际 `404`）
完成时间：2026-04-28 17:57 CST
```

---

## M5-C：后台报名写路由

**前置依赖**：M5-B  
**修改文件**：`apps/group_class_backend/routers/registrations.py`（追加）

### 接口

| 方法 | 路径 | controller |
|---|---|---|
| POST | `/api/v1/admin/registrations/{registration_id}/notes` | `update_registration_notes` |
| POST | `/api/v1/admin/registrations/{registration_id}/status` | `update_registration_status` |

### 自测命令

```bash
# 获取一个 registrationId
REG_ID=$(curl -s "http://127.0.0.1:18000/api/v1/admin/registrations" \
  -H "X-Actor-Id: u_demo_creator" -H "X-Actor-Roles: CLASS_ADMIN" \
  | python3 -c "import sys,json;items=json.load(sys.stdin)['data']['items'];print(items[0]['registrationId']) if items else print('')")

# 更新备注
curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/registrations/$REG_ID/notes" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_demo_creator" -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"followUpNote":"已电话确认","notes":"家长希望周三晚"}' \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['code'] == 'OK'
assert d['data']['followUpNote'] == '已电话确认'
assert d['data']['notes'] == '家长希望周三晚'
print('PASS: 备注更新成功')
"

# 更新状态为 VALID
curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/registrations/$REG_ID/status" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_demo_creator" -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"registrationStatus":"VALID"}' \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['code'] == 'OK'
assert d['data']['registrationStatus'] == 'VALID'
print('PASS: 状态更新为 VALID')
"

# 非法状态值
curl -s -w "\nHTTP:%{http_code}" -X POST "http://127.0.0.1:18000/api/v1/admin/registrations/$REG_ID/status" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_demo_creator" -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"registrationStatus":"INVALID_VALUE"}'
# 期望：HTTP:400

# 无权限
curl -s -w "\nHTTP:%{http_code}" -X POST "http://127.0.0.1:18000/api/v1/admin/registrations/$REG_ID/notes" \
  -H "Content-Type: application/json" -H "X-Actor-Id: u_nobody" \
  -d '{"followUpNote":"无权限测试"}'
# 期望：HTTP:403
```

### 验收标准

- [ ] 更新备注成功，字段持久化（再次查询详情可见）
- [ ] 更新状态为 VALID 成功
- [ ] 非法状态值返回 400
- [ ] 无权限返回 403

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- 更新备注成功，详情再次查询可见
- 更新状态为 `VALID` 成功
- 非法状态值返回 `400`
- 无角色更新备注返回 `403`
完成时间：2026-04-28 17:58 CST
```

---

## M6-A：api.js requestJson Header 注入

**前置依赖**：M2-A（理解 Header 协议即可）  
**修改文件**：`apps/group_class_frontend/js/api.js`

### 改造内容

1. `ApiClient` 构造函数增加 actor 属性读取
2. 新增 `refreshActor()` 方法
3. 修改 `requestJson` 函数签名，统一注入 Header

**改造前的 requestJson**：
```javascript
async function requestJson(url, options = {}) { ... }
```

**改造后**（函数改为接收 actorId 和 actorRoles 参数）：
```javascript
async function requestJson(url, options = {}, actorId = "u_anonymous", actorRoles = []) {
  const mergedHeaders = {
    ...(options.headers || {}),
    "X-Actor-Id": actorId,
    "X-Actor-Roles": actorRoles.join(","),
  };
  const response = await fetch(url, { ...options, headers: mergedHeaders });
  // 其余逻辑不变
}
```

**ApiClient 构造函数改造**：
```javascript
export class ApiClient {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
    this.useMockData = window.localStorage.getItem("GROUP_CLASS_USE_MOCK_DATA") === "true";
    this._loadActor();
  }

  _loadActor() {
    this.actorId = window.localStorage.getItem("GROUP_CLASS_ACTOR_ID") || "u_anonymous";
    this.actorRoles = (window.localStorage.getItem("GROUP_CLASS_ACTOR_ROLES") || "")
      .split(",").map(r => r.trim()).filter(Boolean);
  }

  refreshActor() {
    this._loadActor();
  }

  // 内部调用 requestJson 时传入 this.actorId, this.actorRoles
}
```

### 自测命令

```bash
node --check apps/group_class_frontend/js/api.js
# 期望：无输出（语法通过）
```

### 验收标准

- [ ] `node --check api.js` 通过
- [ ] `requestJson` 函数在所有请求中注入 `X-Actor-Id` 和 `X-Actor-Roles` Header
- [ ] `ApiClient` 有 `refreshActor()` 方法

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- `node --check apps/group_class_frontend/js/api.js` 通过
- `requestJson` 注入 `X-Actor-Id` / `X-Actor-Roles`
- `ApiClient` 已新增 `_loadActor()` 和 `refreshActor()`
完成时间：2026-04-28 18:01 CST
```

---

## M6-B：api.js 各方法清理 actorId

**前置依赖**：M6-A  
**修改文件**：`apps/group_class_frontend/js/api.js`

### 改造内容

将所有 API 方法中的 actorId/actorRoles 从 body 和 URL 移除，改为由 `requestJson` 自动从 Header 注入。

**需要改造的方法列表**：

| 方法 | 改造前 | 改造后 |
|---|---|---|
| `submitReview` | body 含 `actorId, actorRoles: ["INITIATOR"]` | body 只含 `{version}` |
| `approveReview` | body 含 `actorId, actorRoles: ["CLASS_ADMIN"]` | body 只含 `{version}` |
| `rejectReview` | body 含 `actorId, actorRoles: ["CLASS_ADMIN"]` | body 只含 `{version}` |
| `createClass` | payload 可能含 actorId | 移除 actorId |
| `updateClass` | payload 可能含 actorId | 移除 actorId |
| `getAdminRegistrations` | URL 含 `?actorId=...&actorRoles=...` | URL 无 actor 参数 |
| `getAdminRegistrationDetail` | URL 含 actor 参数 | URL 无 actor 参数 |
| `updateRegistrationNotes` | body 含 `actorId, actorRoles` | body 只含业务字段 |
| `updateRegistrationStatus` | body 含 `actorId, actorRoles` | body 只含业务字段 |

**getAdminRegistrations 改造示例**：

改造前：
```javascript
async getAdminRegistrations(actorId, actorRoles) {
  ...
  const roles = (actorRoles || []).join(",");
  const result = await requestJson(
    `${this.baseUrl}/api/v1/admin/registrations?actorId=${encodeURIComponent(actorId)}&actorRoles=${encodeURIComponent(roles)}`
  );
  ...
}
```

改造后：
```javascript
async getAdminRegistrations() {
  if (this.useMockData) { ... }
  const result = await requestJson(
    `${this.baseUrl}/api/v1/admin/registrations`,
    {},
    this.actorId,
    this.actorRoles,
  );
  return result.data || result;
}
```

### 自测命令

```bash
node --check apps/group_class_frontend/js/api.js

# 搜索 body 或 URL 中残留的 actor 字段
rg -n 'JSON\.stringify\([^\n]*(actorId|actorRoles)|actorId=|actorRoles=' apps/group_class_frontend/js/api.js
# 期望：无输出；允许 requestJson 内部使用 actorId/actorRoles 注入 Header
```

### 验收标准

- [ ] `node --check api.js` 通过
- [ ] `requestJson` 可以包含 `actorId`/`actorRoles` 参数并负责注入 Header
- [ ] `actorId`/`actorRoles` 不出现在 `JSON.stringify` body 对象中，也不出现在 URL query 中
- [ ] `getAdminRegistrations()` 和 `getAdminRegistrationDetail()` 方法签名中无 actorId 参数
- [ ] Mock 模式下所有方法仍可正常运行（不依赖后端）

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出（grep 结果）：
- `node --check apps/group_class_frontend/js/api.js` 通过
- `rg 'JSON\.stringify\([^\n]*(actorId|actorRoles)|actorId=|actorRoles=' apps/group_class_frontend/js/api.js` 无输出
- `submitReview` / `approveReview` / `rejectReview` body 只发送 `{version}`
- `getAdminRegistrations()` / `getAdminRegistrationDetail(registrationId)` 已移除 actor 参数
完成时间：2026-04-28 18:01 CST
```

---

## M6-C：app.js 联动更新

**前置依赖**：M6-B  
**修改文件**：`apps/group_class_frontend/js/app.js`

### 改造内容

1. 角色切换后调用 `api.refreshActor()`
2. 删除传递给 api 方法的 actorId/actorRoles 参数
3. 报名详情页的 notes/status 更新 payload 中移除 actorId/actorRoles

**需改动的调用点**：

```javascript
// 改造前
api.getAdminRegistrations(actorId, actorRoles)
api.getAdminRegistrationDetail(registrationId, actorId, actorRoles)
api.updateRegistrationNotes(registrationId, { followUpNote, notes, actorId, actorRoles })
api.updateRegistrationStatus(registrationId, { registrationStatus, actorId, actorRoles })

// 改造后
api.getAdminRegistrations()
api.getAdminRegistrationDetail(registrationId)
api.updateRegistrationNotes(registrationId, { followUpNote, notes })
api.updateRegistrationStatus(registrationId, { registrationStatus })
```

`toggleAdminMode` 函数中追加：
```javascript
function toggleAdminMode() {
  // ... 现有逻辑不变
  api.refreshActor(); // 新增：切换角色后刷新 api 的 actor 信息
}
```

### 自测命令

```bash
node --check apps/group_class_frontend/js/app.js

# 搜索残留的 actorId/actorRoles 参数传递
grep -n "actorId\|actorRoles" apps/group_class_frontend/js/app.js
# 期望：只有 getActorContext() 函数定义和 ACTOR_ID_KEY/ACTOR_ROLES_KEY 常量定义，
#       不应有将 actorId 作为参数传递给 api.xxx() 的调用
```

### 验收标准

- [ ] `node --check app.js` 通过
- [ ] `toggleAdminMode` 中调用了 `api.refreshActor()`
- [ ] app.js 中无向 api 方法传递 actorId/actorRoles 参数的调用
- [ ] `getActorContext()` 函数可保留（用于其他目的），但不传给 api 方法

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- `node --check apps/group_class_frontend/js/app.js` 通过
- `toggleAdminMode()` 和 `renderRoute()` 均调用 `api.refreshActor()`
- API 调用已移除 actorId/actorRoles 参数传递；`getActorContext()` 仅保留用于本地身份读取
完成时间：2026-04-28 18:02 CST
```

---

## M7-A：backend.Dockerfile 更新

**前置依赖**：M5-C  
**修改文件**：`docker/backend.Dockerfile`

### 实现内容

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 先复制依赖文件，利用 Docker 层缓存
COPY pyproject.toml uv.lock ./

# 安装生产依赖（不含 dev group）
RUN uv sync --frozen --no-dev

# 复制应用代码
COPY apps /app/apps

ENV PYTHONPATH=/app
ENV GROUP_CLASS_BACKEND_HOST=0.0.0.0
ENV GROUP_CLASS_BACKEND_PORT=18000

EXPOSE 18000

CMD ["uv", "run", "uvicorn", \
     "apps.group_class_backend.app:app", \
     "--host", "0.0.0.0", \
     "--port", "18000"]
```

### 自测命令

```bash
docker build -f docker/backend.Dockerfile -t group-class-backend-test .
# 期望：build 成功，无报错

docker run --rm -p 18001:18000 group-class-backend-test &
sleep 3
curl -s http://127.0.0.1:18001/health
# 期望：{"status":"ok","version":"0.1.0"}

curl -s http://127.0.0.1:18001/api/v1/public/classes | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['code'] == 'OK'
print('PASS: Docker 容器 API 正常，total:', d['data']['total'])
"

# 清理
docker stop $(docker ps -q --filter ancestor=group-class-backend-test)
```

### 验收标准

- [ ] Docker build 无报错
- [ ] 容器启动后 `/health` 返回 ok
- [ ] 容器内 API 路由正常响应
- [ ] Dockerfile 中无 pip 命令，使用 uv

### 进度记录（Codex 填写）

```
状态：❌ 自测失败（环境阻塞）
自测输出：
- `docker build -f docker/backend.Dockerfile -t group-class-backend-test .`
- 失败：`Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?`
- Dockerfile 已更新为 uv + uvicorn，尚需在 Docker daemon 运行后复测
完成时间：2026-04-28 18:05 CST
```

---

## M7-B：启动脚本更新

**前置依赖**：M7-A  
**修改文件**：`scripts/start-local.sh`、`scripts/stop-local.sh`、`scripts/start-local.ps1`、`scripts/stop-local.ps1`

### 改造内容

**start-local.sh**：将后端启动命令从：
```bash
"${PYTHON_BIN}" -m apps.group_class_backend.server > /tmp/group_class_backend.log 2>&1 &
```
改为：
```bash
uv run uvicorn apps.group_class_backend.app:app \
  --host "${GROUP_CLASS_BACKEND_HOST:-0.0.0.0}" \
  --port "${BACKEND_PORT}" > /tmp/group_class_backend.log 2>&1 &
```

同步更新 `.ps1` 版本（PowerShell 语法对应修改）。

### 自测命令

```bash
# Linux/macOS
chmod +x scripts/start-local.sh scripts/stop-local.sh
./scripts/start-local.sh
sleep 2

curl -s http://127.0.0.1:18000/health
# 期望：{"status":"ok","version":"0.1.0"}

curl -s http://127.0.0.1:5173/ -o /dev/null -w "%{http_code}"
# 期望：200（前端）

./scripts/stop-local.sh
sleep 1
curl -s http://127.0.0.1:18000/health 2>&1
# 期望：连接失败（服务已停止）
```

### 验收标准

- [ ] `start-local.sh` 启动后 `/health` 正常响应
- [ ] 前端 5173 端口正常
- [ ] `stop-local.sh` 成功停止服务
- [ ] 脚本中无 `server.py` 字样

### 进度记录（Codex 填写）

```
状态：❌ 自测失败（当前执行环境限制）
自测输出：
- `./scripts/start-local.sh` 可输出前后端 PID 和 URL
- 当前 Codex 执行环境在命令结束后清理后台子进程，随后 `curl /health` 和前端 5173 均连接失败
- 已将 shell 脚本改为 `nohup` 启动；需要在真实交互 shell 中复测
完成时间：2026-04-28 18:07 CST
```

---

## M8-A：TestClient conftest

**前置依赖**：M5-C  
**修改文件**：`tests/test_api/__init__.py`（新建空文件）、`tests/test_api/conftest.py`（新建）

### 实现内容

```python
# tests/test_api/conftest.py
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from apps.group_class_backend.app import app


@pytest.fixture
def client() -> TestClient:
    """每个测试函数得到一个全新的 TestClient（独立的 AppState）"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_headers() -> dict:
    return {"X-Actor-Id": "u_test_admin", "X-Actor-Roles": "CLASS_ADMIN"}


@pytest.fixture
def initiator_headers() -> dict:
    return {"X-Actor-Id": "u_test_initiator", "X-Actor-Roles": "INITIATOR"}


@pytest.fixture
def public_headers() -> dict:
    return {"X-Actor-Id": "u_public_visitor"}
```

### 自测命令

```bash
# 验证 conftest 可被 pytest 识别
uv run pytest tests/test_api/ --collect-only 2>&1 | head -20
# 期望：no errors，即使暂时没有测试函数也不报错

# 原有测试不受影响
uv run pytest tests/group_class_backend/ -q
# 期望：现有后端测试全部 passed（当前预期约 91 个 pytest case）
```

### 验收标准

- [ ] `tests/test_api/__init__.py` 存在
- [ ] `tests/test_api/conftest.py` 可被 pytest 加载，无报错
- [ ] 现有后端测试仍全部通过

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- `tests/test_api/conftest.py` 已创建，`TestClient(app)` fixture 可加载
- 现有后端测试回归：`91 passed`
- 新增 API 测试创建后，`uv run pytest tests/test_api/ -v` 收集并运行 28 个用例
完成时间：2026-04-28 18:11 CST
```

---

## M8-B：classes API 集成测试

**前置依赖**：M8-A  
**修改文件**：`tests/test_api/test_classes_api.py`（新建）

### 测试用例清单（必须全部实现）

```
TC-C01: 前台列表返回 200，格式正确（requestId/code/data）
TC-C02: 前台列表不含 DRAFT 课程
TC-C03: 前台列表含分页字段（page/total/items）
TC-C04: 后台列表含 DRAFT 课程
TC-C05: 创建课程成功，返回 DRAFT 状态，version=1
TC-C06: 创建课程，creatorId 来自 X-Actor-Id Header
TC-C07: 创建课程缺少 className 返回 400
TC-C08: 更新课程成功，className 改变，version 递增
TC-C09: 更新课程 version 冲突返回 409
TC-C10: 更新不存在的课程返回 404
TC-C11: 审核流：DRAFT → PENDING_REVIEW → OPEN_FOR_ENROLLMENT
TC-C12: 审核通过后课程出现在前台列表
TC-C13: INITIATOR 角色调用 approve 返回 403
TC-C14: 审核驳回：PENDING_REVIEW → REJECTED
TC-C15: REJECTED 课程不在前台列表中
```

### 实现参考（TC-C11 完整示例）

```python
def test_full_review_workflow(client, initiator_headers, admin_headers):
    """TC-C11: 完整审核流"""
    # 创建
    resp = client.post(
        "/api/v1/admin/classes",
        json={"className": "审核流测试", "minStudents": 3},
        headers=initiator_headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    class_id = data["classId"]
    assert data["status"] == "DRAFT"
    assert data["version"] == 1

    # 提交审核
    resp = client.post(
        f"/api/v1/admin/classes/{class_id}/submit-review",
        json={"version": 1},
        headers=initiator_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "PENDING_REVIEW"

    # 审核通过
    resp = client.post(
        f"/api/v1/admin/classes/{class_id}/approve",
        json={"version": 2},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "OPEN_FOR_ENROLLMENT"
    assert resp.json()["data"]["reviewerId"] == "u_test_admin"
```

### 自测命令

```bash
uv run pytest tests/test_api/test_classes_api.py -v
# 期望：15 个用例全部 PASSED
```

### 验收标准

- [ ] TC-C01 至 TC-C15 全部通过
- [ ] 每个测试用例有清晰注释说明测试目的
- [ ] 测试之间相互独立（每次用新的 client fixture）

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
通过用例数：15
自测输出：
- `uv run pytest tests/test_api/test_classes_api.py -v` 作为 `tests/test_api/ -v` 的一部分通过
- TC-C01 至 TC-C15 全部 PASSED
完成时间：2026-04-28 18:11 CST
```

---

## M8-C：registrations API 集成测试

**前置依赖**：M8-A  
**修改文件**：`tests/test_api/test_registrations_api.py`（新建）

### 测试用例清单（必须全部实现）

```
TC-R01: ENROLLMENT 报名成功，registrationId 以 reg- 开头
TC-R02: ENROLLMENT 报名后课程 currentStudents +1
TC-R03: WAITLIST 报名成功，status=WAITLISTED
TC-R04: WAITLIST 报名后课程 waitlistCount +1
TC-R05: 报名到不存在的课程返回 400
TC-R06: ENROLLMENT 报名缺少 studentName 返回 400
TC-R07: 后台报名列表无角色返回 403
TC-R08: 后台报名列表有 CLASS_ADMIN 角色返回 200
TC-R09: 报名详情字段完整（parentName/contactInfo/studentName）
TC-R10: 更新备注成功，字段持久化（再次查询可见）
TC-R11: 更新状态为 VALID 成功
TC-R12: 更新状态为非法值返回 400
TC-R13: 无权限更新备注返回 403
```

### 辅助 fixture 参考

```python
@pytest.fixture
def approved_class_id(client, initiator_headers, admin_headers) -> str:
    """创建并审核通过一个课程，返回其 classId"""
    resp = client.post("/api/v1/admin/classes",
        json={"className": "报名测试课", "minStudents": 3, "maxStudents": 10},
        headers=initiator_headers)
    class_id = resp.json()["data"]["classId"]
    version = resp.json()["data"]["version"]
    client.post(f"/api/v1/admin/classes/{class_id}/submit-review",
        json={"version": version}, headers=initiator_headers)
    client.post(f"/api/v1/admin/classes/{class_id}/approve",
        json={"version": version + 1}, headers=admin_headers)
    return class_id
```

### 自测命令

```bash
uv run pytest tests/test_api/test_registrations_api.py -v
# 期望：13 个用例全部 PASSED

# 全量测试
uv run pytest tests/ -q
# 期望：全部 passed（当前预期约 91 个现有 case + 15 + 13）
```

### 验收标准

- [ ] TC-R01 至 TC-R13 全部通过
- [ ] 全量测试（含现有后端测试）全部通过
- [ ] 无 fixture 泄漏（各测试相互独立）

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
通过用例数：13
全量测试结果：`uv run pytest tests/ -q` -> `119 passed in 0.23s`
完成时间：2026-04-28 18:11 CST
```

---

## M9：server.py 删除 + 文档同步

**前置依赖**：M8-C（全量测试通过）  
**修改文件**：`apps/group_class_backend/server.py`（删除）、`CLAUDE.md`（更新）、`README.md`（更新）、`docs/development-and-deployment.md`（更新）、`docs/local-startup-guide.md`（更新）、相关计划文档（按需更新或标注历史）

### 执行步骤

**步骤 1**：确认全量测试通过
```bash
uv run pytest tests/ -q
# 必须全部通过才能继续
```

**步骤 2**：删除 server.py
```bash
git rm apps/group_class_backend/server.py
```

**步骤 3**：更新 CLAUDE.md

将「Commands」章节的启动命令替换为：

````markdown
### 运行后端

```bash
uv run uvicorn apps.group_class_backend.app:app --host 0.0.0.0 --port 18000 --reload
```

### 运行测试

```bash
# 全部测试
uv run pytest tests/ -q

# 单个文件
uv run pytest tests/group_class_backend/classes/test_create_class_draft.py -q

# API 集成测试
uv run pytest tests/test_api/ -v
```

### 前端语法检查

```bash
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js
```
````

将「Architecture - Backend」章节更新以下内容：

- HTTP 层：FastAPI + uvicorn（替代原 `http.server.ThreadingHTTPServer`）
- 入口文件：`apps/group_class_backend/app.py`
- 依赖注入：`apps/group_class_backend/deps.py`，`ActorContext` 从 `X-Actor-Id`/`X-Actor-Roles` Header 解析
- 路由文件：`apps/group_class_backend/routers/classes.py`、`routers/registrations.py`
- 后期替换认证：只需修改 `deps.py` 中的 `get_actor` 函数

**步骤 4**：更新 README.md，将启动命令改为 uv 版本

**步骤 5**：同步其他文档中的旧入口引用

需要处理的文档：

- `docs/development-and-deployment.md`
- `docs/local-startup-guide.md`
- `docs/integration-selftest-2026-04-13.md`
- `docs/plans/2026-04-27-next-phase-dev-plan.md`

处理规则：

- 仍作为当前开发指南使用的文档：更新为 FastAPI/uvicorn 入口
- 明显属于历史记录或历史验收的文档：保留原文，但在文档顶部补充“历史记录，迁移后入口已变更”的说明

### 自测命令

```bash
# server.py 不存在
ls apps/group_class_backend/server.py 2>&1
# 期望：No such file or directory

# 全量测试仍通过
uv run pytest tests/ -q
# 期望：全部通过

# 脚本启动仍正常
./scripts/start-local.sh
sleep 2
curl -s http://127.0.0.1:18000/health
./scripts/stop-local.sh

# CLAUDE.md 中无 server.py
grep -n "server.py" CLAUDE.md
# 期望：无输出

# README.md 中无旧启动命令
grep -n "python -m apps.group_class_backend.server" README.md
# 期望：无输出

# 当前开发文档中无旧启动命令
grep -n "python -m apps.group_class_backend.server\\|from apps.group_class_backend.server import run" \
  docs/development-and-deployment.md docs/local-startup-guide.md
# 期望：无输出
```

### 验收标准

- [ ] `server.py` 文件不存在
- [ ] 全量测试通过
- [ ] CLAUDE.md 启动命令已更新为 uv 版本
- [ ] CLAUDE.md 架构描述已更新（含 deps.py、routers/ 说明）
- [ ] README.md 无旧启动命令
- [ ] 当前开发指南无旧 `server.py` 启动入口；历史文档如保留旧入口，已明确标注为历史记录

### 进度记录（Codex 填写）

```
状态：✅ 自测通过
自测输出：
- `apps/group_class_backend/server.py` 已删除
- `uv run pytest tests/ -q` -> `119 passed in 0.24s`
- `node --check apps/group_class_frontend/js/api.js` 和 `app.js` 均通过
- `CLAUDE.md` / `README.md` / 当前开发指南已更新为 FastAPI + uvicorn 入口
- 当前开发文档、scripts、docker 中无旧 `apps.group_class_backend.server` / `server.py` 启动入口
完成时间：2026-04-28 18:16 CST
```

---

## Claude 总体验收清单

**触发条件**：Codex 声明全部 M1-M9 任务完成，进度总览表全部为 ✅。  
**执行者**：Claude  
**目标**：独立验证，不依赖 Codex 的自测报告。

### 第一层：静态检查

```bash
# 1. 文件结构检查
ls apps/group_class_backend/app.py          # 必须存在
ls apps/group_class_backend/deps.py         # 必须存在
ls apps/group_class_backend/routers/classes.py      # 必须存在
ls apps/group_class_backend/routers/registrations.py # 必须存在
ls apps/group_class_backend/server.py 2>&1  # 必须不存在

# 2. uv 配置
ls pyproject.toml uv.lock .python-version   # 全部必须存在

# 3. 前端语法
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js

# 4. actor 清理验证：body/URL 中无 actorId/actorRoles，Header 注入除外
rg -n 'JSON\.stringify\([^\n]*(actorId|actorRoles)|actorId=|actorRoles=' apps/group_class_frontend/js/api.js
# 期望：无输出
```

### 第二层：测试回归

```bash
# 全量测试（含现有后端测试 + 新增 ≥28 个 API 集成测试）
uv run pytest tests/ -v 2>&1 | tail -20
# 期望：全部 PASSED，预计 ≥119 passed；若现有参数化 case 数变化，以 pytest 实际 collect 数 + 新增 28 个为准

# 单独跑集成测试
uv run pytest tests/test_api/ -v
# 期望：≥28 passed
```

### 第三层：端到端业务链路

```bash
# 启动服务
uv run uvicorn apps.group_class_backend.app:app --host 127.0.0.1 --port 18000 &
sleep 2

# 链路 1：健康检查
curl -s http://127.0.0.1:18000/health | python3 -c "
import sys, json; d = json.load(sys.stdin)
assert d['status'] == 'ok'; print('✓ health ok')
"

# 链路 2：前台看板（种子数据）
curl -s http://127.0.0.1:18000/api/v1/public/classes | python3 -c "
import sys, json; d = json.load(sys.stdin)
assert d['code'] == 'OK'
items = d['data']['items']
assert len(items) >= 2, f'期望≥2条公开课程，实际{len(items)}'
assert all(i['status'] != 'DRAFT' for i in items), 'DRAFT不应出现在前台'
print('✓ 前台列表:', len(items), '条，无DRAFT')
"

# 链路 3：创建 → 审核通过 → 前台可见
CLASS_ID=$(curl -s -X POST http://127.0.0.1:18000/api/v1/admin/classes \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_e2e_test" -H "X-Actor-Roles: INITIATOR" \
  -d '{"className":"端到端验收班","minStudents":3}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['classId'])")
echo "✓ 创建课程: $CLASS_ID"

curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID/submit-review" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_e2e_test" -H "X-Actor-Roles: INITIATOR" \
  -d '{"version":1}' | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert d['data']['status']=='PENDING_REVIEW'; print('✓ 提交审核成功')
"

curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID/approve" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_e2e_admin" -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"version":2}' | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert d['data']['status']=='OPEN_FOR_ENROLLMENT'
assert d['data']['reviewerId']=='u_e2e_admin'
print('✓ 审核通过，reviewerId 正确')
"

# 链路 4：报名
REG_ID=$(curl -s -X POST http://127.0.0.1:18000/api/v1/public/registrations \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_e2e_parent" \
  -d "{\"classId\":\"$CLASS_ID\",\"registerType\":\"ENROLLMENT\",\"parentName\":\"验收家长\",\"contactInfo\":\"13800138000\",\"studentName\":\"验收学员\",\"studentGrade\":\"三年级\"}" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['data']['registrationId'])")
echo "✓ 报名成功: $REG_ID"

# 链路 5：后台查看报名
curl -s "http://127.0.0.1:18000/api/v1/admin/registrations" \
  -H "X-Actor-Id: u_e2e_admin" -H "X-Actor-Roles: CLASS_ADMIN" \
  | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']=='OK'
ids=[i['registrationId'] for i in d['data']['items']]
assert '$REG_ID' in ids, f'报名记录应在列表中'
print('✓ 后台可见报名记录')
"

# 链路 6：权限验证
STATUS=$(curl -s -w "%{http_code}" -o /dev/null \
  "http://127.0.0.1:18000/api/v1/admin/registrations" \
  -H "X-Actor-Id: u_nobody")
[ "$STATUS" = "403" ] && echo "✓ 无权限返回403" || echo "✗ 期望403，实际$STATUS"

# 链路 7：Header 协议验证（请求体不含 actorId）
RESP=$(curl -s -X POST "http://127.0.0.1:18000/api/v1/admin/classes/$CLASS_ID/update" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_e2e_admin" -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"version":3,"className":"Header协议验证"}')
echo $RESP | python3 -c "
import sys,json; d=json.load(sys.stdin)
assert d['code']=='OK', f'更新失败：{d}'
print('✓ Header 协议正确，body 无需 actorId')
"

# 停止服务
kill $(lsof -ti:18000) 2>/dev/null
```

### 第四层：代码质量审查

Claude 人工检查以下内容：

- [ ] `deps.py`：`get_actor` 函数签名和 `ActorContext` 定义正确
- [ ] `app.py`：`lifespan` 正确，种子数据完整（3个课程），`get_state()` 有断言保护
- [ ] `routers/classes.py`：9 条路由全部实现（M3-A、M3-B、M4-A、M4-B、M4-C），无业务逻辑
- [ ] `routers/registrations.py`：5条路由全部实现，无业务逻辑
- [ ] `_http_status()` 错误码映射完整（OK→200, NOT_FOUND→404, PERMISSION_DENIED→403, VERSION_CONFLICT→409）
- [ ] controller 调用参数与签名完全匹配（无缺失、无多余）
- [ ] `api.js`：body 和 URL 中无 actorId/actorRoles 残留
- [ ] `app.js`：`toggleAdminMode` 调用了 `api.refreshActor()`
- [ ] 集成测试：每个 TC 编号对应的断言逻辑正确，测试之间独立

### 验收结论模板

```
## Claude 总体验收结论

验收日期：
总测试数：（预计 ≥119；以 pytest 实际 collect 数为准）

### 静态检查：PASS / FAIL
- 文件结构：
- 前端语法：
- actor 清理：

### 测试回归：PASS / FAIL
- 原有后端测试：
- 新增集成测试：

### 端到端链路：PASS / FAIL
- health: 
- 前台看板:
- 创建→审核→前台可见:
- 报名:
- 后台报名管理:
- 权限拒绝:
- Header 协议:

### 代码质量：PASS / FAIL
- 重要发现：

### 最终结论：GO / HOLD
HOLD 原因（若有）：
```
