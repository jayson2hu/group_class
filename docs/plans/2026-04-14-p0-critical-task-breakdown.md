# P0-Critical 功能细分任务书

Date: 2026-04-14
Status: Ready for Codex Execution
Owner: Hermes
Depends on: docs/plans/2026-04-14-gap-analysis.md

---

## 执行说明

- 共 5 个模块、19 个独立任务，按编号顺序执行
- 每个任务完成后必须执行自测并记录结果
- 验收标准全部通过后该任务才算完成
- 前置依赖标注为"无"的任务可独立执行

---

## Codex 开发进度与验收记录（2026-04-14）

### 1) 开发完成情况（按 A1 → E2）

| 任务 | 状态 | 实施结果 |
|---|---|---|
| A1 | 已完成 | `server.py` 新增 `POST /api/v1/admin/classes`，接入 `create_class_draft`。 |
| A2 | 已完成 | `server.py` 新增 `POST /api/v1/admin/classes/{classId}/update`，接入 `update_class_draft`。 |
| A3 | 已完成 | `server.py` 新增审核三路由：`submit-review` / `approve` / `reject`，完成错误码到 HTTP 状态映射。 |
| A4 | 已完成 | `server.py` 新增报名列表/详情 GET 路由，支持 `actorId`、`actorRoles` query 解析。 |
| A5 | 已完成 | `server.py` 新增报名备注与状态更新 POST 路由。 |
| B1 | 已完成 | `api.js` 新增 `createClass`、`updateClass`，真实接口与 mock 分支均实现。 |
| B2 | 已完成 | `app.js` 新增 `#/admin/classes/new` 创建页与表单提交逻辑。 |
| B3 | 已完成 | `app.js` 新增 `#/admin/classes/{classId}/edit` 编辑页、回填与提交更新。 |
| B4 | 已完成 | `app.js` 路由注册已补齐；后台课程列表新增“新建课程”和“编辑”入口。 |
| C1 | 已完成 | `api.js` 新增 `submitReview`、`approveReview`、`rejectReview`，含 mock。 |
| C2 | 已完成 | `app.js` 后台详情页接入审核操作按钮、confirm、失败 alert、刷新。 |
| C3 | 已完成 | `app.js` 后台列表动作列将 `submit_review/approve/reject` 渲染为按钮并可快捷执行。 |
| D1 | 已完成 | `api.js` 新增报名管理 4 个接口：列表、详情、备注、状态更新。 |
| D2 | 已完成 | `app.js` 新增 `#/admin/registrations` 报名列表页。 |
| D3 | 已完成 | `app.js` 新增 `#/admin/registrations/{registrationId}` 详情页及备注/状态更新交互。 |
| D4 | 已完成 | `index.html` 新增“报名管理”导航；`app.js` 新增报名管理路由匹配。 |
| E1 | 已完成 | `index.html` 导航拆分为 public/admin 两组，后台组默认隐藏；新增角色切换按钮。 |
| E2 | 已完成 | `app.js` 新增角色切换机制、admin 路由守卫、localStorage 持久化与 admin 身份默认值联动。 |

### 2) 自测执行结果

#### 2.1 自动化回归

- 命令：`$env:PYTHONPATH='d:/vscodefile/group_class'; D:/software/anacond/python.exe -m pytest tests/group_class_backend -q`
- 结果：`91 passed in 0.13s`（通过，满足“≥85 passed”）

#### 2.2 前端静态校验

- 命令：`node --check apps/group_class_frontend/js/api.js` → 通过
- 命令：`node --check apps/group_class_frontend/js/app.js` → 通过

#### 2.3 接口链路验收（后端启动 + API 端到端）

执行方式：启动 `apps.group_class_backend.server`（端口 `18000`），按文档链路执行创建课程 → 编辑 → 提交审核 → 审核通过 → 前台可见 → 提交报名 → 后台列表/详情 → 更新备注/状态。

关键结果：

- `createStatus = DRAFT`（A1 通过）
- `updateClassName = acceptance-class-updated`（A2 通过）
- `submitStatus = PENDING_REVIEW`（A3-提交审核通过）
- `approveStatus = OPEN_FOR_ENROLLMENT`（A3-审核通过）
- `publicVisible = true`（审核通过后前台可见）
- `regSubmitCode = OK`（前台报名提交成功）
- `registrationListFound = true`（A4 报名列表可查）
- `regDetailParent = Tom`（A4 报名详情可查）
- `noteFollowUp = called`（A5 备注更新成功）
- `regStatus = VALID`（A5 状态更新成功）

#### 2.4 负向验收（错误分支）

- 缺少 `className/templateId` 创建课程：HTTP `400`，返回 `code=VALIDATION_INVALID_ARGUMENT`
- 非 `CLASS_ADMIN` 审核通过：HTTP `403`
- 更新不存在课程：HTTP `404`
- 报名状态传非法值：HTTP `400`

#### 2.5 前端入口可达性验证

启动前端静态服务后检查首页 HTML：

- `id="admin-nav"` 存在
- `id="role-toggle"` 存在
- `#/admin/registrations` 导航链接存在

说明：此项验证了导航结构产出；完整浏览器点击流（3.1-3.10 的纯 UI 操作）仍建议人工走查一遍。

### 3) 当前验收结论

- 结论：`Conditional-Go`
- 代码实现层面：A1-E2 已全部落地。
- 自动化与接口验收层面：后端回归、核心接口链路、负向分支均通过。
- 剩余风险：浏览器可视化交互（按钮点击、跳转、刷新后的 UI 呈现）未做自动化录制，建议按 3.1-3.10 做一次人工 UI 回归后发布。

---

## 模块 A：后端路由补齐

将已实现的 9 个控制器函数接入 `apps/group_class_backend/server.py` HTTP 层。

---

### A1：课程创建路由

任务编号：A1
修改文件：`apps/group_class_backend/server.py`
前置依赖：无

接口契约：
- 方法：`POST /api/v1/admin/classes`
- 请求体：JSON，字段对齐 `create_class_draft` 参数（className, classType, priceAmount, minStudents, maxStudents 等）
- 请求体额外字段：`actorId`（字符串，创建人 ID）
- 成功响应：HTTP 200，body 为 `success_response` 格式，`data` 含完整课程对象
- 失败响应：HTTP 400，body 为 `error_response` 格式

实现要点：
- 在 `server.py` 顶部新增 `from apps.group_class_backend.classes.controller import create_class_draft`
- 在 `do_POST` 方法中新增路由匹配 `path == "/api/v1/admin/classes"`
- 调用 `create_class_draft(payload=body, repository=self.state.class_repository, audit_writer=self.state.audit_writer, request_id=request_id, actor_id=body.get("actorId", "u_admin"), now=datetime.now(timezone.utc))`
- 根据返回的 `code` 字段判断 HTTP 状态码

自测要求：
```bash
# 启动后端
python -m apps.group_class_backend.server

# 创建课程
curl -X POST http://127.0.0.1:8000/api/v1/admin/classes \
  -H "Content-Type: application/json" \
  -d '{"className":"测试拼课班","classType":"GROUP_CLASS","priceAmount":1999,"minStudents":6,"maxStudents":8,"actorId":"u_test"}'
```

验收标准：
1. 返回 HTTP 200，响应 JSON 含 `data.classId`、`data.status` 为 `"DRAFT"`
2. 缺少 className 和 templateId 时返回 HTTP 400，`code` 为 `"VALIDATION_INVALID_ARGUMENT"`
3. `GET /api/v1/admin/classes` 列表中能看到新创建的课程

---

### A2：课程更新路由

任务编号：A2
修改文件：`apps/group_class_backend/server.py`
前置依赖：A1

接口契约：
- 方法：`POST /api/v1/admin/classes/{classId}/update`
- 请求体：JSON，含 `version`（必填）、可选更新字段（className, priceAmount 等）、`actorId`
- 成功响应：HTTP 200，`data` 含更新后课程对象
- 版本冲突：HTTP 409，`code` 为 `"CLASS_VERSION_CONFLICT"`
- 课程不存在：HTTP 404

实现要点：
- 新增 `from apps.group_class_backend.classes.controller import update_class_draft`
- 路由匹配：`path` 以 `/api/v1/admin/classes/` 开头且以 `/update` 结尾
- 从 path 中提取 classId
- 调用 `update_class_draft(class_id=class_id, payload=body, repository=..., audit_writer=..., request_id=..., actor_id=body.get("actorId","u_admin"), now=...)`

自测要求：
```bash
# 先通过 A1 创建课程，记录返回的 classId 和 version
# 更新课程名称
curl -X POST http://127.0.0.1:8000/api/v1/admin/classes/{classId}/update \
  -H "Content-Type: application/json" \
  -d '{"version":1,"className":"更新后的班名","actorId":"u_test"}'
```

验收标准：
1. 返回 HTTP 200，`data.className` 为 `"更新后的班名"`，`data.version` 递增或不变
2. version 不匹配时返回 HTTP 409
3. classId 不存在时返回 HTTP 404

---

### A3：审核流三条路由

任务编号：A3
修改文件：`apps/group_class_backend/server.py`
前置依赖：A1

接口契约（3 条路由，统一在本任务实现）：

路由 1：`POST /api/v1/admin/classes/{classId}/submit-review`
- 请求体：`{ "version": int, "actorId": str, "actorRoles": ["INITIATOR"] }`
- 成功：HTTP 200，`data.status` 变为 `"PENDING_REVIEW"`
- 非法状态：HTTP 400

路由 2：`POST /api/v1/admin/classes/{classId}/approve`
- 请求体：`{ "version": int, "actorId": str, "actorRoles": ["CLASS_ADMIN"] }`
- 成功：HTTP 200，`data.status` 变为 `"OPEN_FOR_ENROLLMENT"`
- 权限不足：HTTP 403

路由 3：`POST /api/v1/admin/classes/{classId}/reject`
- 请求体：`{ "version": int, "actorId": str, "actorRoles": ["CLASS_ADMIN"] }`
- 成功：HTTP 200，`data.status` 变为 `"REJECTED"`

实现要点：
- 新增 import：`submit_class_review, approve_class_review, reject_class_review`
- 在 `do_POST` 中按 path 后缀分发：`/submit-review`、`/approve`、`/reject`
- 每个调用传入 `actor_roles=body.get("actorRoles")`
- HTTP 状态码映射：`PERMISSION_DENIED` → 403，`CLASS_VERSION_CONFLICT` → 409，`CLASS_NOT_FOUND` → 404，其他错误 → 400

自测要求：
```bash
# 1. 创建课程（A1），记录 classId、version
# 2. 提交审核
curl -X POST http://127.0.0.1:8000/api/v1/admin/classes/{classId}/submit-review \
  -H "Content-Type: application/json" \
  -d '{"version":1,"actorId":"u_test","actorRoles":["INITIATOR"]}'
# 3. 审核通过
curl -X POST http://127.0.0.1:8000/api/v1/admin/classes/{classId}/approve \
  -H "Content-Type: application/json" \
  -d '{"version":1,"actorId":"u_admin","actorRoles":["CLASS_ADMIN"]}'
# 4. 验证前台可见
curl http://127.0.0.1:8000/api/v1/public/classes
```

验收标准：
1. 提交审核后 status 变为 `PENDING_REVIEW`
2. 审核通过后 status 变为 `OPEN_FOR_ENROLLMENT`
3. 审核通过的课程出现在 `GET /api/v1/public/classes` 列表中
4. 无 CLASS_ADMIN 角色调用 approve 返回 HTTP 403
5. 驳回后 status 变为 `REJECTED`，前台不可见

---

### A4：报名管理读路由

任务编号：A4
修改文件：`apps/group_class_backend/server.py`
前置依赖：无

接口契约：

路由 1：`GET /api/v1/admin/registrations?actorId=xxx&actorRoles=CLASS_ADMIN`
- 成功：HTTP 200，`data.items` 为报名记录数组
- 权限不足：HTTP 403

路由 2：`GET /api/v1/admin/registrations/{registrationId}?actorId=xxx&actorRoles=CLASS_ADMIN`
- 成功：HTTP 200，`data` 含报名详情
- 不存在：HTTP 404

实现要点：
- 新增 import：`list_registrations, get_registration_detail`
- 在 `do_GET` 中新增两条路由
- 从 query string 解析 `actorId` 和 `actorRoles`（actorRoles 用逗号分隔）
- 使用 `urllib.parse.parse_qs` 解析查询参数

自测要求：
```bash
# 先通过前台报名接口创建一条报名记录
curl -X POST http://127.0.0.1:8000/api/v1/public/registrations \
  -H "Content-Type: application/json" \
  -d '{"classId":"{已有课程ID}","registerType":"ENROLLMENT","parentName":"张三","contactInfo":"13800138000","studentName":"小明","studentGrade":"三年级","englishLevel":"基础"}'

# 查询报名列表
curl "http://127.0.0.1:8000/api/v1/admin/registrations?actorId=u_demo_creator&actorRoles=CLASS_ADMIN"

# 查询报名详情
curl "http://127.0.0.1:8000/api/v1/admin/registrations/{registrationId}?actorId=u_demo_creator&actorRoles=CLASS_ADMIN"
```

验收标准：
1. 报名列表返回 HTTP 200，`data.items` 含已提交的报名记录
2. 报名详情返回 HTTP 200，含 parentName、studentName、contactInfo 等字段
3. 无权限时返回 HTTP 403
4. registrationId 不存在时返回 HTTP 404

---

### A5：报名管理写路由

任务编号：A5
修改文件：`apps/group_class_backend/server.py`
前置依赖：A4

接口契约：

路由 1：`POST /api/v1/admin/registrations/{registrationId}/notes`
- 请求体：`{ "followUpNote": str, "notes": str, "actorId": str, "actorRoles": ["CLASS_ADMIN"] }`
- 成功：HTTP 200，`data` 含更新后报名详情

路由 2：`POST /api/v1/admin/registrations/{registrationId}/status`
- 请求体：`{ "registrationStatus": "VALID"|"INVALID"|"CANCELLED", "actorId": str, "actorRoles": ["CLASS_ADMIN"] }`
- 成功：HTTP 200，`data.registrationStatus` 为新状态

实现要点：
- 新增 import：`update_registration_notes, update_registration_status`
- 在 `do_POST` 中新增两条路由，按 path 后缀 `/notes` 和 `/status` 分发
- 传入 `class_repository` 和 `registration_repository`

自测要求：
```bash
# 更新备注
curl -X POST http://127.0.0.1:8000/api/v1/admin/registrations/{registrationId}/notes \
  -H "Content-Type: application/json" \
  -d '{"followUpNote":"已电话确认","notes":"家长希望周三上课","actorId":"u_admin","actorRoles":["CLASS_ADMIN"]}'

# 更新状态
curl -X POST http://127.0.0.1:8000/api/v1/admin/registrations/{registrationId}/status \
  -H "Content-Type: application/json" \
  -d '{"registrationStatus":"VALID","actorId":"u_admin","actorRoles":["CLASS_ADMIN"]}'
```

验收标准：
1. 备注更新后返回 HTTP 200，`data.followUpNote` 为 `"已电话确认"`
2. 状态更新后返回 HTTP 200，`data.registrationStatus` 为 `"VALID"`
3. 非法状态值返回 HTTP 400
4. 无权限返回 HTTP 403

---

## 模块 B：后台创建/编辑课程页

让运营可以通过浏览器 UI 创建和编辑课程，不再依赖 curl。

---

### B1：api.js 新增课程写入方法

任务编号：B1
修改文件：`apps/group_class_frontend/js/api.js`
前置依赖：A1, A2

新增方法签名：

```javascript
// 创建课程
async createClass(payload) → { classId, className, status, ... }
// payload: { className, classType, priceAmount, minStudents, maxStudents, ... , actorId }

// 更新课程
async updateClass(classId, payload) → { classId, className, status, version, ... }
// payload: { version, className?, priceAmount?, ... , actorId }
```

实现要点：
- `createClass`：`POST ${this.baseUrl}/api/v1/admin/classes`，body 为 JSON
- `updateClass`：`POST ${this.baseUrl}/api/v1/admin/classes/${classId}/update`，body 为 JSON
- 两个方法都返回 `result.data || result`
- mock 模式下返回合理的假数据（classId 用 `cls_${Date.now()}`，status 为 `"DRAFT"`）

自测要求：
- 在浏览器控制台执行 `const api = new ApiClient("http://127.0.0.1:8000"); await api.createClass({className:"控制台测试",classType:"GROUP_CLASS",priceAmount:999,minStudents:4,maxStudents:6,actorId:"u_test"})`
- 确认返回对象含 classId

验收标准：
1. `createClass` 调用成功返回含 `classId` 和 `status: "DRAFT"` 的对象
2. `updateClass` 调用成功返回更新后的课程对象
3. mock 模式下两个方法均可正常返回假数据

---

### B2：后台创建课程页面

任务编号：B2
修改文件：`apps/group_class_frontend/js/app.js`, `apps/group_class_frontend/css/styles.css`
前置依赖：B1

页面路由：`#/admin/classes/new`

页面结构：
- hero 区：标题"创建新课程"，说明文案
- 表单分三组：
  - 基础信息：className（必填）、classType（下拉：GROUP_CLASS/TRIAL/NORMAL）、courseSubtitle、priceAmount、depositAmount
  - 拼课规则：minStudents、maxStudents、sessionCount、scheduleSummary、startDate、endDate、signupDeadline
  - 展示文案：targetAudience、unsuitableAudience、courseGoal、groupRule、absenceRule、waitlistRule、failureRule、faqSummary
- 提交栏：「保存草稿」按钮 + 「返回列表」链接

实现要点：
- 新增 `renderAdminCreateClass()` 函数
- 复用现有 `form-section`、`form-grid`、`form-submit-bar` 样式类
- 表单提交调用 `api.createClass(payload)`
- 成功后跳转到 `#/admin/classes/{classId}`（后台详情页）
- 失败时在表单底部显示错误信息

自测要求：
- 浏览器打开 `http://127.0.0.1:35330/#/admin/classes/new`
- 填写 className 和 classType，点击保存草稿
- 确认跳转到后台详情页

验收标准：
1. 页面正常渲染，三组表单字段完整展示
2. className 为空时提交被浏览器原生校验拦截（required 属性）
3. 填写必填字段后提交成功，跳转到后台详情页
4. 后台课程列表中能看到新创建的课程

---

### B3：后台编辑课程页面

任务编号：B3
修改文件：`apps/group_class_frontend/js/app.js`, `apps/group_class_frontend/js/api.js`
前置依赖：B2

页面路由：`#/admin/classes/{classId}/edit`

页面结构：
- 与 B2 创建页结构一致，但标题改为"编辑课程"
- 页面加载时调用 `api.getAdminClassDetail(classId)` 回填所有字段
- 提交时调用 `api.updateClass(classId, payload)`，payload 必须包含 `version`

实现要点：
- 新增 `renderAdminEditClass(classId)` 函数
- 复用 B2 的表单模板，抽取为 `adminClassFormTemplate(detail, isEdit)` 共享函数
- 回填逻辑：遍历 detail 对象，将值设置到对应 input 的 value/selected
- version 作为 hidden input 存储
- 成功后跳转到 `#/admin/classes/{classId}`

自测要求：
- 浏览器打开 `http://127.0.0.1:35330/#/admin/classes/{已有classId}/edit`
- 确认字段已回填
- 修改 className，点击保存
- 确认跳转到详情页，名称已更新

验收标准：
1. 页面加载后所有已有字段正确回填
2. 修改字段后提交成功，详情页显示更新后的值
3. version 不匹配时显示错误提示（模拟：在另一个标签页先更新一次）

---

### B4：路由注册与列表页入口

任务编号：B4
修改文件：`apps/group_class_frontend/js/app.js`
前置依赖：B2, B3

实现要点：
- 在 `renderRoute()` 中新增路由匹配：
  - `parts[0]==="admin" && parts[1]==="classes" && parts[2]==="new"` → `renderAdminCreateClass()`
  - `parts[0]==="admin" && parts[1]==="classes" && parts[3]==="edit"` → `renderAdminEditClass(parts[2])`
- 注意：`new` 路由必须在 `parts[2]` 通配详情路由之前匹配
- 在 `renderAdminClasses()` 的 hero 区新增「新建课程」按钮：`<a class="btn primary" href="#/admin/classes/new">新建课程</a>`
- 在后台课程列表每行新增「编辑」链接：`<a class="btn" href="#/admin/classes/${id}/edit">编辑</a>`

自测要求：
- 打开后台课程列表，确认"新建课程"按钮可见
- 点击"新建课程"跳转到创建页
- 点击某课程的"编辑"跳转到编辑页

验收标准：
1. 后台列表页显示"新建课程"按钮
2. 点击后正确跳转到 `#/admin/classes/new`
3. 每行课程有"编辑"入口，点击跳转到 `#/admin/classes/{id}/edit`
4. 路由不冲突：`/new` 不会被当作 classId 处理

---

## 模块 C：后台审核操作 UI

让管理员可以在浏览器中完成提交审核、审核通过、审核驳回操作。

---

### C1：api.js 新增审核方法

任务编号：C1
修改文件：`apps/group_class_frontend/js/api.js`
前置依赖：A3

新增方法签名：

```javascript
// 提交审核
async submitReview(classId, version, actorId) → { classId, status, ... }

// 审核通过
async approveReview(classId, version, actorId) → { classId, status, ... }

// 审核驳回
async rejectReview(classId, version, actorId) → { classId, status, ... }
```

实现要点：
- `submitReview`：`POST /api/v1/admin/classes/${classId}/submit-review`，body `{ version, actorId, actorRoles: ["INITIATOR"] }`
- `approveReview`：`POST /api/v1/admin/classes/${classId}/approve`，body `{ version, actorId, actorRoles: ["CLASS_ADMIN"] }`
- `rejectReview`：`POST /api/v1/admin/classes/${classId}/reject`，body `{ version, actorId, actorRoles: ["CLASS_ADMIN"] }`
- 三个方法都返回 `result.data || result`
- mock 模式下返回 status 分别为 `PENDING_REVIEW`、`OPEN_FOR_ENROLLMENT`、`REJECTED`

自测要求：
- 浏览器控制台调用 `await api.submitReview("{classId}", 1, "u_test")` 确认返回

验收标准：
1. 三个方法调用后端成功，返回正确的 status
2. mock 模式下三个方法均可正常返回

---

### C2：后台详情页审核操作按钮

任务编号：C2
修改文件：`apps/group_class_frontend/js/app.js`
前置依赖：C1

实现要点：
- 修改 `renderAdminClassDetail(classId)` 函数
- 根据 `detail.status` 和 `detail.actions` 动态渲染操作按钮：
  - status 为 `DRAFT` 或 `REJECTED` 时显示「提交审核」按钮
  - status 为 `PENDING_REVIEW` 时显示「审核通过」和「驳回」按钮
  - 其他状态不显示审核按钮
- 按钮点击时弹出 `confirm()` 确认对话框
- 确认后调用对应 api 方法，传入 `detail.version` 和 actorId（从 localStorage 读取，默认 `"u_admin"`）
- 操作成功后刷新当前页面（重新调用 `renderAdminClassDetail`）
- 操作失败时 alert 错误信息

按钮位置：放在后台详情页 hero 区的 `admin-detail-actions` 区域内

自测要求：
- 创建一个草稿课程，打开后台详情页
- 确认显示「提交审核」按钮
- 点击提交审核，确认状态变为 PENDING_REVIEW
- 确认按钮变为「审核通过」和「驳回」
- 点击审核通过，确认状态变为 OPEN_FOR_ENROLLMENT
- 前台看板确认该课程可见

验收标准：
1. DRAFT 状态详情页显示「提交审核」按钮
2. 点击提交审核后页面刷新，状态变为 PENDING_REVIEW，按钮变为「审核通过」「驳回」
3. 审核通过后状态变为 OPEN_FOR_ENROLLMENT，前台可见
4. 驳回后状态变为 REJECTED，按钮恢复为「提交审核」
5. 每次操作前有 confirm 确认

---

### C3：后台列表页审核快捷操作

任务编号：C3
修改文件：`apps/group_class_frontend/js/app.js`
前置依赖：C2

实现要点：
- 修改 `renderAdminClasses()` 中的表格行渲染
- 将 action tag 中的 `submit_review`、`approve`、`reject` 渲染为可点击按钮（而非纯文本 span）
- 点击后弹出 confirm，确认后调用对应 api 方法
- 需要先获取该课程的 version：调用 `api.getAdminClassDetail(classId)` 获取最新 version
- 操作成功后刷新列表（重新调用 `renderAdminClasses`）

自测要求：
- 后台列表页，DRAFT 课程行的动作列显示可点击的「submit_review」按钮
- 点击后确认状态变化，列表刷新

验收标准：
1. 动作列中 submit_review / approve / reject 显示为可点击按钮样式
2. 点击 submit_review 后列表刷新，该课程状态变为 PENDING_REVIEW
3. 其他非审核动作（view、edit）保持原有文本样式

---

## 模块 D：后台报名管理页

让运营可以在浏览器中查看报名列表、报名详情、更新备注和状态。

---

### D1：api.js 新增报名管理方法

任务编号：D1
修改文件：`apps/group_class_frontend/js/api.js`
前置依赖：A4, A5

新增方法签名：

```javascript
// 报名列表
async getAdminRegistrations(actorId, actorRoles) → { items: [...] }

// 报名详情
async getAdminRegistrationDetail(registrationId, actorId, actorRoles) → { registrationId, parentName, ... }

// 更新备注
async updateRegistrationNotes(registrationId, payload) → { registrationId, followUpNote, ... }
// payload: { followUpNote, notes, actorId, actorRoles }

// 更新状态
async updateRegistrationStatus(registrationId, payload) → { registrationId, registrationStatus, ... }
// payload: { registrationStatus, actorId, actorRoles }
```

实现要点：
- `getAdminRegistrations`：`GET /api/v1/admin/registrations?actorId=${actorId}&actorRoles=${actorRoles.join(",")}`
- `getAdminRegistrationDetail`：`GET /api/v1/admin/registrations/${registrationId}?actorId=${actorId}&actorRoles=${actorRoles.join(",")}`
- `updateRegistrationNotes`：`POST /api/v1/admin/registrations/${registrationId}/notes`，body 为 JSON
- `updateRegistrationStatus`：`POST /api/v1/admin/registrations/${registrationId}/status`，body 为 JSON
- mock 模式下返回合理假数据

自测要求：
- 浏览器控制台调用 `await api.getAdminRegistrations("u_demo_creator", ["CLASS_ADMIN"])` 确认返回

验收标准：
1. 四个方法调用后端成功，返回格式正确
2. mock 模式下四个方法均可正常返回

---

### D2：后台报名列表页

任务编号：D2
修改文件：`apps/group_class_frontend/js/app.js`, `apps/group_class_frontend/css/styles.css`
前置依赖：D1

页面路由：`#/admin/registrations`

页面结构：
- hero 区：标题"报名管理"，说明文案，报名总数 summary pill
- 表格面板，列：报名编号、课程名称、报名类型、家长姓名、学员姓名、学员年级、联系方式、报名状态、提交时间、操作
- 操作列：「查看」链接跳转到 `#/admin/registrations/{registrationId}`
- actorId 和 actorRoles 从 localStorage 读取（key: `GROUP_CLASS_ACTOR_ID` 默认 `"u_demo_creator"`，`GROUP_CLASS_ACTOR_ROLES` 默认 `"CLASS_ADMIN"`）

实现要点：
- 新增 `renderAdminRegistrations()` 函数
- 复用现有 `admin-hero`、`admin-table-panel`、`table-wrap`、`admin-table` 样式
- 报名类型显示中文：ENROLLMENT → 报名、WAITLIST → 候补、TRIAL → 试听
- 报名状态用 `statusChip` 渲染

自测要求：
- 先通过前台提交一条报名
- 打开 `http://127.0.0.1:35330/#/admin/registrations`
- 确认表格中显示该报名记录

验收标准：
1. 页面正常渲染，表格列完整
2. 报名记录数据与前台提交一致
3. 报名类型和状态正确显示中文/标签
4. 无报名时显示"暂无数据"

---

### D3：后台报名详情页

任务编号：D3
修改文件：`apps/group_class_frontend/js/app.js`, `apps/group_class_frontend/css/styles.css`
前置依赖：D2

页面路由：`#/admin/registrations/{registrationId}`

页面结构：
- hero 区：标题"报名详情"，报名编号、课程名称、报名类型
- 信息面板：家长姓名、联系方式、学员姓名、学员年级、英语基础、备注、提交时间
- 操作面板：
  - 跟进备注：textarea，「保存备注」按钮，调用 `api.updateRegistrationNotes`
  - 状态管理：下拉选择（VALID/INVALID/CANCELLED），「更新状态」按钮，调用 `api.updateRegistrationStatus`
- 底部：「返回报名列表」链接

实现要点：
- 新增 `renderAdminRegistrationDetail(registrationId)` 函数
- 页面加载时调用 `api.getAdminRegistrationDetail` 获取数据
- 备注保存和状态更新成功后刷新页面
- actorId / actorRoles 同 D2 从 localStorage 读取

自测要求：
- 从报名列表点击"查看"进入详情页
- 确认信息完整展示
- 输入跟进备注，点击保存，确认保存成功
- 选择状态为 VALID，点击更新，确认状态变化

验收标准：
1. 详情页正确展示所有报名字段
2. 保存备注后刷新页面，备注内容保留
3. 更新状态后刷新页面，状态标签变化
4. 返回列表链接正常工作

---

### D4：导航与路由注册

任务编号：D4
修改文件：`apps/group_class_frontend/index.html`, `apps/group_class_frontend/js/app.js`
前置依赖：D2, D3

实现要点：
- 在 `index.html` 导航栏新增：`<a href="#/admin/registrations" class="nav-link">报名管理</a>`，放在"后台课程管理"链接之后
- 在 `app.js` 的 `renderRoute()` 中新增路由匹配：
  - `parts[0]==="admin" && parts[1]==="registrations" && !parts[2]` → `renderAdminRegistrations()`
  - `parts[0]==="admin" && parts[1]==="registrations" && parts[2]` → `renderAdminRegistrationDetail(parts[2])`
- 在 `syncNavState()` 中确保 `#/admin/registrations` 路由能正确激活导航项

自测要求：
- 打开页面，确认导航栏显示"报名管理"
- 点击跳转到报名列表页
- 导航激活态正确

验收标准：
1. 导航栏显示"报名管理"链接
2. 点击后跳转到 `#/admin/registrations`
3. 导航激活态随路由正确切换
4. 报名详情页路由正常工作

---

## 模块 E：前后台导航隔离

普通用户（家长）不应看到后台管理入口。

---

### E1：导航栏拆分与默认隐藏

任务编号：E1
修改文件：`apps/group_class_frontend/index.html`, `apps/group_class_frontend/css/styles.css`
前置依赖：D4

实现要点：
- 将 `index.html` 导航栏拆为两组：
  ```html
  <nav class="nav">
    <div class="container nav-inner">
      <div class="nav-group nav-public">
        <a href="#/public/classes" class="nav-link">前台看板</a>
      </div>
      <div class="nav-group nav-admin" id="admin-nav" style="display:none">
        <a href="#/admin/classes" class="nav-link">课程管理</a>
        <a href="#/admin/registrations" class="nav-link">报名管理</a>
      </div>
      <button class="nav-role-toggle" id="role-toggle" type="button">切换为管理员</button>
    </div>
  </nav>
  ```
- `nav-admin` 默认 `display:none`
- 在 `styles.css` 中为 `nav-role-toggle` 添加样式：小号按钮，右对齐，半透明

自测要求：
- 打开页面，确认只看到"前台看板"，后台链接不可见
- 确认"切换为管理员"按钮可见

验收标准：
1. 默认状态下后台导航链接不可见
2. 前台看板链接正常可见
3. 角色切换按钮可见

---

### E2：角色切换机制

任务编号：E2
修改文件：`apps/group_class_frontend/js/app.js`
前置依赖：E1

实现要点：
- 在 `app.js` 顶部新增角色管理逻辑：
  ```javascript
  function isAdminMode() {
    return window.localStorage.getItem("GROUP_CLASS_ROLE") === "admin";
  }
  function toggleAdminMode() {
    const current = isAdminMode();
    window.localStorage.setItem("GROUP_CLASS_ROLE", current ? "public" : "admin");
    syncAdminNav();
    // 如果从 admin 切回 public 且当前在后台路由，跳转到前台
    if (current && window.location.hash.startsWith("#/admin")) {
      window.location.hash = "#/public/classes";
    }
  }
  function syncAdminNav() {
    const adminNav = document.getElementById("admin-nav");
    const toggleBtn = document.getElementById("role-toggle");
    if (adminNav) adminNav.style.display = isAdminMode() ? "" : "none";
    if (toggleBtn) toggleBtn.textContent = isAdminMode() ? "切换为家长" : "切换为管理员";
  }
  ```
- 页面加载时调用 `syncAdminNav()`
- 为 `#role-toggle` 绑定 click 事件调用 `toggleAdminMode()`
- 在 `renderRoute()` 开头增加守卫：如果非 admin 模式访问 `#/admin/*` 路由，自动跳转到 `#/public/classes`
- actorId / actorRoles 联动：admin 模式下 `GROUP_CLASS_ACTOR_ID` 默认 `"u_demo_creator"`，`GROUP_CLASS_ACTOR_ROLES` 默认 `"CLASS_ADMIN"`

自测要求：
- 打开页面，默认为家长模式，后台导航不可见
- 点击"切换为管理员"，后台导航出现
- 手动输入 `#/admin/classes` 在家长模式下被重定向到前台
- 切换回家长模式，如果当前在后台页面则自动跳转前台

验收标准：
1. 默认家长模式，后台导航隐藏
2. 点击切换后后台导航显示，按钮文案变为"切换为家长"
3. 家长模式下直接访问 `#/admin/*` 被重定向到 `#/public/classes`
4. 刷新页面后角色状态保持（localStorage 持久化）
5. 从管理员切回家长时，如在后台页面则自动跳转

---

## 执行总览

| 编号 | 任务名称 | 模块 | 修改文件 | 前置依赖 |
|---|---|---|---|---|
| A1 | 课程创建路由 | 后端路由 | server.py | 无 |
| A2 | 课程更新路由 | 后端路由 | server.py | A1 |
| A3 | 审核流三条路由 | 后端路由 | server.py | A1 |
| A4 | 报名管理读路由 | 后端路由 | server.py | 无 |
| A5 | 报名管理写路由 | 后端路由 | server.py | A4 |
| B1 | api.js 课程写入方法 | 创建/编辑页 | api.js | A1, A2 |
| B2 | 后台创建课程页 | 创建/编辑页 | app.js, styles.css | B1 |
| B3 | 后台编辑课程页 | 创建/编辑页 | app.js, api.js | B2 |
| B4 | 路由注册与列表入口 | 创建/编辑页 | app.js | B2, B3 |
| C1 | api.js 审核方法 | 审核 UI | api.js | A3 |
| C2 | 详情页审核按钮 | 审核 UI | app.js | C1 |
| C3 | 列表页审核快捷操作 | 审核 UI | app.js | C2 |
| D1 | api.js 报名管理方法 | 报名管理 | api.js | A4, A5 |
| D2 | 后台报名列表页 | 报名管理 | app.js, styles.css | D1 |
| D3 | 后台报名详情页 | 报名管理 | app.js, styles.css | D2 |
| D4 | 导航与路由注册 | 报名管理 | index.html, app.js | D2, D3 |
| E1 | 导航栏拆分与隐藏 | 导航隔离 | index.html, styles.css | D4 |
| E2 | 角色切换机制 | 导航隔离 | app.js | E1 |

推荐执行顺序：A1 → A2 → A3 → A4 → A5 → B1 → B2 → B3 → B4 → C1 → C2 → C3 → D1 → D2 → D3 → D4 → E1 → E2

---

## 全量回归验收

所有 18 个任务完成后，执行端到端验收：

```bash
# 1. 后端测试回归
python -m pytest tests/group_class_backend -q

# 2. 启动后端
python -m apps.group_class_backend.server

# 3. 端到端业务链路验证（按顺序）
# 3.1 切换为管理员模式
# 3.2 后台创建课程 → 保存草稿
# 3.3 后台编辑课程 → 修改字段
# 3.4 后台详情页 → 提交审核
# 3.5 后台详情页 → 审核通过
# 3.6 切换为家长模式 → 前台看板看到课程
# 3.7 前台详情页 → 点击报名
# 3.8 填写报名表 → 提交成功
# 3.9 切换为管理员 → 报名管理 → 看到报名记录
# 3.10 报名详情 → 更新备注 → 标记有效
```

通过标准：
1. pytest 全量通过（≥85 passed）
2. 上述 3.1-3.10 全部可在浏览器中走通
3. 家长模式下后台入口不可见
4. 家长模式下直接访问后台 URL 被重定向
