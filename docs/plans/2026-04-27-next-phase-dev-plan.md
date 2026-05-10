# 拼课系统下一阶段开发计划

Date: 2026-04-27  
Status: In Progress  
Owner: Jayson  
Review: Claude  
Depends on: docs/plans/2026-04-14-gap-analysis.md（P0-Critical 已全部完成，前端重设计已全部完成）

---

## 当前状态总结

### 已完成（截至 2026-04-28）

**后端 API（148 tests passed）**
- FastAPI routers 已覆盖 classes CRUD、审核流、课程取消、注册 CRUD、报名导出、模板 CRUD
- 两套仓储：InMemory（运行态）+ SQLite（测试用）
- 权限模型：INITIATOR / CLASS_ADMIN / SUPER_ADMIN
- AuditWriter（NullAuditWriter，结构已定，未持久化）

**前端（app.js 1186行，api.js 695行）**
- 前台：看板、详情、报名表单（ENROLLMENT/WAITLIST/TRIAL）、报名成功页、底部 FAQ
- 后台：课程列表、创建、编辑、详情（含审核）、模板列表/创建/编辑、报名列表、报名详情（含备注+状态）
- 交互：Toast 通知、空/错误状态统一、角色切换（家长/管理员）、路由守卫

### 验收结论（Conditional-Go）

代码层面完整，自动化回归通过，剩余人工 UI 走查建议执行一遍后再发布。

---

## 下一阶段功能清单与优先级

### P0-Important（MVP 体验完整，本阶段必做）

| 编号 | 功能 | 范围 | 状态 |
|---|---|---|---|
| G1 | 课程下架 / 取消状态流转 | 后端 + 前端 | ✅ 已完成 |
| G2 | 候补表单字段独立化 | 前端 | ✅ 已完成 |
| G3 | 前端错误提示增强 | 前端 | ✅ 已完成 |
| G4 | 分页参数透传 | 后端 + 前端 | ✅ 已完成 |
| G5 | 报名成功页：展示课程当前状态 | 前端 | ✅ 已完成 |

### P1（运营增强，可延后）

| 编号 | 功能 | 范围 | 状态 |
|---|---|---|---|
| H1 | 模板 CRUD 后端接口 | 后端 | ✅ 已完成 |
| H2 | 模板管理前端页面 | 前端 | ✅ 已完成 |
| H3 | 报名导出（CSV） | 后端 + 前端 | ✅ 已完成 |
| H4 | 课程筛选 / 搜索 | 后端 + 前端 | ✅ 已完成 |
| H5 | 自动状态计算（60% 成班规则） | 后端 | ✅ 已完成 |
| H6 | 候补转正流程 | 后端 + 前端 | ✅ 已完成 |
| H7 | 课程封面 / 亮点 / 负责人字段 | 后端 + 前端 | ⬜ 待开始 |
| H8 | 分享链接（复制到剪贴板） | 前端 | ⬜ 待开始 |

### P2（业务闭环，暂不纳入）

- 支付锁位 / 支付状态
- 报名截止自动关闭定时任务
- 认证 / 鉴权中间件（真实 JWT）
- 自动通知（短信 / 微信）

---

## P0-Important 详细任务书

### G1：课程下架 / 取消状态流转

**背景**  
PRD 7.5 要求运营可以对已发布课程执行"下架"或"取消"操作。当前 `ClassStatus` 枚举已包含 `CANCELLED`，但后端无对应控制器方法，FastAPI routers 无路由，前端无按钮。

**范围**  
修改文件：`apps/group_class_backend/classes/controller.py`、`apps/group_class_backend/routers/classes.py`、`apps/group_class_frontend/js/api.js`、`apps/group_class_frontend/js/app.js`

**接口契约**

路由：`POST /api/v1/admin/classes/{classId}/cancel`  
请求体：`{ "version": int }`，身份通过 `X-Actor-Id` / `X-Actor-Roles` Header 传递  
成功：HTTP 200，`data.status = "CANCELLED"`  
权限不足：HTTP 403  
非法状态（DRAFT/ENDED 不可取消）：HTTP 400

**后端实现要点**
- 在 `controller.py` 新增 `cancel_class` 函数，逻辑与 `reject_class_review` 类似
- 允许取消的状态：`OPEN_FOR_ENROLLMENT`、`ALMOST_CONFIRMED`、`CONFIRMED`、`FULL`、`WAITLIST_OPEN`、`IN_PROGRESS`
- 只有 `CLASS_ADMIN` / `SUPER_ADMIN` 可操作（INITIATOR 不可）
- 在 `routers/classes.py` 中新增 FastAPI 路由
- 写 AuditEvent（action `"class.cancelled"`）

**前端实现要点**
- `api.js` 新增 `cancelClass(classId, version)` 方法，身份通过统一 Header 注入
- `app.js` 后台详情页操作区：当 `status` 为可取消状态时显示「取消课程」按钮（红色危险样式）
- 点击后 confirm 弹窗（「确认取消本课程？此操作不可撤销。」）
- 成功后 toast 提示 + 刷新详情页
- 取消后课程前台不可见（CANCELLED 不在 `_PUBLIC_VISIBLE_STATUSES` 中）

**自测命令**
```bash
# 启动后端
uv run uvicorn apps.group_class_backend.app:app --host 0.0.0.0 --port 18000 --reload

# 将一个课程审核通过（status=OPEN_FOR_ENROLLMENT），然后取消
curl -X POST http://127.0.0.1:18000/api/v1/admin/classes/{classId}/cancel \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: u_admin" \
  -H "X-Actor-Roles: CLASS_ADMIN" \
  -d '{"version":2}'
```

**验收标准**
1. 调用后 status 变为 `CANCELLED`，HTTP 200
2. INITIATOR 角色调用返回 HTTP 403
3. DRAFT 状态调用返回 HTTP 400
4. 取消后前台看板不可见该课程
5. 后台详情页 toast 提示「课程已取消」
6. pytest 全量通过

**完成记录（2026-04-28）**

- 后端新增 `cancel_class` controller 和 `POST /api/v1/admin/classes/{classId}/cancel`
- 前端新增 `api.cancelClass()`，后台详情和课程列表操作区支持取消课程
- 新增/更新 controller 与 API 集成测试
- 自测：`uv run pytest tests/ -q` -> `125 passed`；`node --check api.js/app.js` 通过

---

### G2：候补表单字段独立化

**背景**  
PRD 7.4 定义候补（WAITLIST）报名表单与正式报名（ENROLLMENT）字段集不同：候补需要额外确认"是否接受相近课程推荐"（`acceptSimilarRecommendation`），学员姓名为选填（PRD 定义可不填），英语基础为选填。当前候补复用同一表单，缺少专属字段。

**范围**  
修改文件：`apps/group_class_frontend/js/app.js`、`apps/group_class_frontend/css/styles.css`

**实现要点**
- 修改 `enrollmentFormHtml(classId, registerType)` 函数
- WAITLIST 模式下：
  - 在「补充说明」分组底部新增 checkbox：`是否愿意接受相近课程的推荐（勾选后运营可优先为你匹配其他课程）`
  - 学员姓名和英语基础去掉 `required` 属性，标签改为「学员姓名（选填）」
  - 表单 hero 区标题改为「加入候补」，副文案改为「满员后将按照提交顺序通知，请确认联系方式准确」
  - 流程说明侧栏文案调整为候补流程（提交 → 等待空位 → 运营通知 → 确认转正）
- 提交时将 checkbox 值作为 `acceptSimilarRecommendation` 字段传入 payload
- ENROLLMENT 表单不变

**自测要求**
- 找一个 `FULL` 状态课程，点击「加入候补」进入表单
- 确认标题为「加入候补」，学员姓名为选填，底部有推荐 checkbox
- 不填学员姓名直接提交，确认成功
- 勾选 checkbox 提交，确认 `acceptSimilarRecommendation` 字段传入

**验收标准**
1. WAITLIST 表单有独立标题和副文案
2. WAITLIST 表单有「接受相近推荐」checkbox
3. WAITLIST 学员姓名选填，不填可提交
4. ENROLLMENT 表单无变化
5. checkbox 值正确传入 API payload

**完成记录（2026-04-28）**

- WAITLIST 表单标题改为「加入候补」，副文案改为满员候补通知说明
- 学员姓名和英语基础在 WAITLIST 模式下显示为选填，去除 required
- 新增 `acceptSimilarRecommendation` checkbox，并在 WAITLIST 提交 payload 中传入布尔值
- mock 报名记录保留 `acceptSimilarRecommendation`
- 自测：`node --check api.js/app.js` 通过；关键文案/字段 `rg` 检查通过；`uv run pytest tests/ -q` -> `125 passed`

---

### G3：前端错误提示增强

**背景**  
当前前端 API 错误统一显示 toast「操作失败」，不展示后端返回的具体 `details[0].message`，运营无法得知失败原因。

**范围**  
修改文件：`apps/group_class_frontend/js/api.js`、`apps/group_class_frontend/js/app.js`

**实现要点**

**api.js 改动**  
`requestJson` 函数已解析 `result?.details?.[0]?.message`，但 `message` 中有时是英文技术信息（如 `"className or templateId is required"`）。  
新增中文错误映射函数 `translateErrorMessage(rawMessage)` 在 `api.js` 中：

```javascript
const ERROR_MAP = {
  "className or templateId is required": "课程名称或模板 ID 为必填",
  "version does not match current resource": "课程已被他人修改，请刷新后重试",
  "only DRAFT or REJECTED classes can be submitted for review": "仅草稿或已驳回课程可提交审核",
  "only PENDING_REVIEW classes can be approved": "仅待审核课程可审核通过",
  "only PENDING_REVIEW classes can be rejected": "仅待审核课程可驳回",
  "only CLASS_ADMIN or SUPER_ADMIN can approve class review": "无审核权限，请使用管理员账号",
  "only CLASS_ADMIN or SUPER_ADMIN can reject class review": "无审核权限，请使用管理员账号",
  "class status does not accept ENROLLMENT registration": "当前课程状态不接受报名",
  "class status does not accept WAITLIST registration": "当前课程状态不接受候补",
  "class not found": "课程不存在",
  "registration not found": "报名记录不存在",
};
export function translateErrorMessage(msg) {
  return ERROR_MAP[msg] || msg;
}
```

**app.js 改动**  
所有 catch 块中调用 `showToast(translateErrorMessage(err.message), "error")` 替换当前的固定文案。

**验收标准**
1. version 冲突时 toast 显示「课程已被他人修改，请刷新后重试」
2. 权限不足时 toast 显示「无审核权限」
3. 已知错误有中文提示，未知错误直接显示原始英文
4. api.js 语法检查通过（`node --check`）

**完成记录（2026-04-28）**

- `api.js` 新增 `translateErrorMessage()` 和常见后端错误中文映射
- `requestJson()` 抛出的 `Error.message` 已使用中文映射，现有 `app.js` catch/toast 自动展示中文错误
- 自测：`node --check api.js/app.js` 通过；映射函数验证 version 冲突、权限不足、未知错误；`uv run pytest tests/ -q` -> `125 passed`

---

### G4：分页参数透传

**背景**  
当前 FastAPI classes 路由已透传课程分页参数；报名列表仍需补充分页参数。当记录超过单页容量时，前端也需要分页控件。

**范围**  
修改文件：`apps/group_class_backend/routers/classes.py`、`apps/group_class_backend/routers/registrations.py`、`apps/group_class_frontend/js/api.js`、`apps/group_class_frontend/js/app.js`

**后端实现要点**
- 在 `GET /api/v1/public/classes` 和 `GET /api/v1/admin/classes` 中解析查询参数 `page`（默认 1）和 `pageSize`（默认 20，最大 100）
- `list_classes` 已支持 page/page_size 参数，只需透传
- 响应已含 `total` 字段，可在前端用于显示「第 X 页 / 共 Y 条」

**前端实现要点**
- `api.js` 中 `getPublicClasses(page=1, pageSize=20)` 和 `getAdminClasses(page=1, pageSize=20)` 增加参数，请求 URL 追加 `?page=X&pageSize=Y`
- `app.js` 在看板和后台课程列表底部新增分页控件：
  ```
  [< 上一页]  第 1 / 3 页  [下一页 >]
  ```
  - 首页时隐藏「上一页」，末页时隐藏「下一页」
  - 控件样式复用 `btn` class，两端排列

**验收标准**
1. `GET /api/v1/public/classes?page=1&pageSize=5` 返回前 5 条，`page=2` 返回 6-10 条
2. `total` 字段正确反映总数
3. 前台看板底部分页控件可见，翻页后列表更新
4. 后台课程列表同上
5. pageSize 超过 100 时后端截断为 100

**完成记录（2026-04-28）**

- classes 路由支持 `page_size` 与 `pageSize` 两种查询参数，`pageSize` 超过 100 时后端截断为 100
- admin registrations 补齐分页参数和 `{page,pageSize,total,items}` 响应结构
- 前台看板、后台课程列表、后台报名列表从 hash query 读取 `page`，底部渲染上一页/下一页分页控件
- 自测：`node --check api.js/app.js` 通过；`uv run pytest tests/ -q` -> `128 passed`

---

### G5：报名成功页展示课程状态

**背景**  
PRD 7.3 要求报名成功页展示「课程当前状态」，以便家长了解是否已成班（如还差几人成班）。当前成功页有 `classStatus` 字段但未渲染进度信息。

**范围**  
修改文件：`apps/group_class_frontend/js/app.js`

**实现要点**
- 修改 `renderEnrollmentSuccess(result, classId)` 函数
- 在成功页「报名信息」卡片中新增一行：
  - 标签：「课程状态」
  - 值：根据 `result.classStatus` 映射中文（同前台 `_STATUS_LABELS`）
- 额外调用 `api.getPublicClassDetail(classId)` 获取 `progressText`（如「还差 2 人成班」），展示在「后续说明」卡片的副文案位置
- 若 `classStatus` 为 `FULL` 或 `WAITLIST_OPEN`，展示「您已加入候补，如有空位将尽快通知」提示

**验收标准**
1. 报名成功页显示课程当前状态（中文）
2. ENROLLMENT 报名显示 progressText
3. WAITLIST 报名显示候补说明文案
4. classId 对应课程不存在时页面不崩溃（静默失败）

**完成记录（2026-04-28）**

- `renderEnrollmentSuccess()` 改为异步拉取课程详情，展示 `progressText`，详情获取失败时静默降级
- 成功页课程状态改为中文状态标签，覆盖报名中、即将成班、已满员、候补开放等状态
- `FULL` / `WAITLIST_OPEN` 状态下追加候补说明文案
- 自测：`node --check api.js/app.js` 通过；`uv run pytest tests/ -q` -> `128 passed`

---

## P1 任务简述（供 Codex 后续执行）

### H1：模板 CRUD 后端接口

**新增**：`TemplateRepository` 实现（InMemory + SQLite）、`create_template` / `update_template` / `list_templates` / `get_template` 控制器函数。  
**路由**：`POST /api/v1/admin/templates`、`GET /api/v1/admin/templates`、`GET /api/v1/admin/templates/{id}`、`POST /api/v1/admin/templates/{id}/update`。  
**验收**：对应 pytest 测试全部通过。

**完成记录（2026-04-28）**

- 新增 templates 模块：InMemory/SQLite 仓储、CRUD 控制器、4 条 admin FastAPI 路由
- 扩展 `class_templates` 表字段，覆盖课程模板默认值，并保留模板名唯一索引
- 课程创建路由已接入 AppState 中的模板仓储，可通过 `templateId` 继承模板默认值
- 自测：模板专项 `11 passed`；`uv run pytest tests/ -q` -> `139 passed`

---

### H2：模板管理前端页面

**前置**：H1  
**路由**：`#/admin/templates`、`#/admin/templates/new`、`#/admin/templates/{id}/edit`  
**页面**：列表（模板名 / 类型 / 状态 / 操作）、创建表单、编辑表单。  
**验收**：可通过 UI 完整创建和编辑模板，创建课程时模板下拉可选。

**完成记录（2026-04-28）**

- 后台导航新增模板管理入口，支持模板列表、创建、编辑三类页面
- 前端 API 新增模板列表/详情/创建/更新方法，mock 模式同步支持模板 CRUD
- 创建课程表单新增模板下拉；从模板列表「用模板建课」会预选对应模板
- 自测：`node --check api.js/app.js` 通过；`uv run pytest tests/ -q` -> `139 passed`

---

### H3：报名导出（CSV）

**后端**：新增 `GET /api/v1/admin/registrations/export`，身份通过 `X-Actor-Id` / `X-Actor-Roles` Header 传递，响应 `Content-Type: text/csv`，文件名为 `registrations_{timestamp}.csv`。  
**前端**：报名列表页 hero 区新增「导出 CSV」按钮，点击触发下载。  
**验收**：下载的 CSV 文件包含所有可见报名记录，字段与列表页一致。

**完成记录（2026-04-28）**

- 后端新增 `export_registrations_csv()`，复用报名列表权限和可见范围，使用 `csv.DictWriter` 输出 CSV
- 新增 `GET /api/v1/admin/registrations/export`，返回 `text/csv` 与 `Content-Disposition` 附件文件名
- 前端报名列表新增「导出 CSV」按钮，真实模式和 mock 模式均可下载
- 自测：报名 API 专项 `16 passed`；`node --check api.js/app.js` 通过；`uv run pytest tests/ -q` -> `141 passed`

---

### H4：课程筛选 / 搜索

**后端**：`list_classes` 新增 `status_filter`（可多选）、`creator_id_filter`、`keyword`（匹配 class_name）参数。  
**前端**：后台课程列表页新增筛选栏（状态多选下拉 + 搜索输入框），改变时重新请求。  
**验收**：按状态筛选后列表只显示对应状态课程；关键字搜索按课程名过滤。

**完成记录（2026-05-09）**

- 后端 `GET /api/v1/admin/classes` 支持 `status`、`creatorId`、`keyword` 查询参数，并与分页共同工作
- 前端后台课程列表新增状态、关键词、发起人 ID 筛选栏，筛选条件同步到 hash query
- mock 模式同步支持状态和关键词筛选
- 自测：课程 API 专项 `23 passed`；`node --check api.js/app.js` 通过；`uv run pytest tests/ -q` -> `144 passed`

---

### H5：自动状态计算（60% 成班规则）

**背景**：PRD 8.3 建议当报名人数 ≥ 60% × max_students 时自动切换为 `ALMOST_CONFIRMED`，≥ 100% 时切换为 `FULL`。  
**后端**：在 `registrations/controller.py` 的 `submit_registration` 成功后，根据 `current_students / max_students` 比例更新课程状态（仅当当前状态为 `OPEN_FOR_ENROLLMENT`）。  
**验收**：第 5 人报名（6 人班）后课程自动变 `ALMOST_CONFIRMED`；第 6 人后变 `FULL`。

**完成记录（2026-05-09）**

- ENROLLMENT 报名成功后按 `current_students / max_students` 自动计算课程状态
- `OPEN_FOR_ENROLLMENT` 下达到满员时切换 `FULL`，达到成班阈值时切换 `ALMOST_CONFIRMED`
- 报名成功响应中的 `classStatus` 返回更新后的课程状态
- 自测：报名控制器专项 `19 passed`；`uv run pytest tests/ -q` -> `146 passed`

---

### H6：候补转正流程

**背景**：当一个报名被取消（status → CANCELLED）时，如有候补，运营应能将候补转为正式报名。  
**后端**：新增 `POST /api/v1/admin/registrations/{id}/promote-from-waitlist`，将候补报名状态改为 `VALID`，同时 `current_students + 1`，`waitlist_count - 1`。  
**前端**：报名详情页，当 `registerType == WAITLIST && registrationStatus == WAITLISTED` 时显示「转为正式报名」按钮。  
**验收**：转正后报名状态变 `VALID`，课程人数 +1，候补人数 -1。

**完成记录（2026-05-09）**

- 后端新增 `promote_waitlist_registration()` 与 `POST /api/v1/admin/registrations/{id}/promote-from-waitlist`
- 转正后报名状态变 `VALID`，课程 `currentStudents + 1`，`waitlistCount - 1`
- 前端报名详情页对 `WAITLISTED` 候补记录显示「转为正式报名」按钮
- 自测：报名专项 `37 passed`；`node --check api.js/app.js` 通过；`uv run pytest tests/ -q` -> `148 passed`

---

### H7：课程封面 / 亮点 / 负责人字段

**后端**：`GroupClass` 模型新增 `cover_image_url`（str | None）、`highlights`（str | None）、`owner_id`（str | None）；同步更新 schema DDL、仓储 SQL、`_MUTABLE_FIELD_MAP`、序列化函数。  
**前端**：创建/编辑表单新增三个字段；前台详情页 hero 区展示封面图（img 标签，src 为 cover_image_url）；课程亮点在详情页单独成区域。  
**验收**：字段可写入、可读取；封面图字段为空时不渲染 img 标签。

---

### H8：分享链接

**前端**：前台课程详情页右侧侧栏新增「复制分享链接」按钮，点击后将当前 URL 写入剪贴板（`navigator.clipboard.writeText`），toast 提示「链接已复制」。  
**降级**：若 clipboard API 不可用（HTTP 环境），展示输入框让用户手动复制。  
**验收**：HTTPS 环境下点击后 toast 提示，粘贴内容为课程详情页 URL。

---

## 开发执行规则

### Codex 执行规范

1. **单功能单 commit**：每完成一个编号（G1/G2...）提交一次，commit message 格式：`feat(G1): 课程下架取消状态流转`
2. **后端改动必须有测试**：每个新增控制器方法在 `tests/` 中有对应测试用例
3. **先测试再提交**：后端改动后运行 `PYTHONPATH=$(pwd) python3 -m pytest tests/group_class_backend -q`，全部通过才提交
4. **前端改动必须 node --check**：`node --check apps/group_class_frontend/js/api.js && node --check apps/group_class_frontend/js/app.js`
5. **不引入外部依赖**：后端仅用 Python 标准库，前端仅用原生 JS/CSS，无 npm 包

### Review 规则（Claude 执行）

每个功能完成后，Claude 会检查：

1. 后端：控制器逻辑是否正确、权限检查是否完整、测试是否覆盖正向+负向
2. 前端：API 调用参数是否与后端契约一致、mock 模式是否可用、错误处理是否完整
3. 回归：pytest 全量通过、node --check 通过
4. 不改动已完成功能的测试

---

## 全量验收检查单（本阶段完成后执行）

```
# 自动化
PYTHONPATH=$(pwd) python3 -m pytest tests/group_class_backend -q   # 期望：全部通过
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js

# G1 课程取消
- 后台创建课程 → 审核通过 → 取消课程
- 前台看板确认课程不可见
- INITIATOR 取消返回 403

# G2 候补表单
- 找满员课程 → 进入候补表单
- 确认「接受推荐」checkbox 存在
- 不填学员姓名提交成功

# G3 错误提示
- version 冲突场景：toast 显示中文

# G4 分页
- 后台列表 pageSize=5 翻页正常
- 前台看板分页控件可见

# G5 报名成功页
- 报名成功后显示课程状态中文

# 原有功能回归（不可退步）
- 完整业务链路：创建 → 审核 → 报名 → 管理
- 家长/管理员模式切换
- 路由守卫
```

---

## 文件变更矩阵（预估）

| 功能 | 后端文件 | 前端文件 |
|---|---|---|
| G1 课程取消 | controller.py, routers/classes.py | api.js, app.js |
| G2 候补表单 | — | app.js, styles.css |
| G3 错误提示 | — | api.js, app.js |
| G4 分页 | routers/classes.py, routers/registrations.py | api.js, app.js, styles.css |
| G5 成功页 | — | app.js |
| H1 模板 CRUD | controller.py, repository.py, routers/*.py | — |
| H2 模板前端 | — | api.js, app.js, index.html |
| H3 导出 CSV | routers/registrations.py | api.js, app.js |
| H4 筛选搜索 | controller.py, routers/*.py | api.js, app.js, styles.css |
| H5 自动状态 | registrations/controller.py | — |
| H6 候补转正 | registrations/controller.py, routers/registrations.py | api.js, app.js |
| H7 封面字段 | models/group_class.py, persistence/schema.py, classes/controller.py | api.js, app.js, styles.css |
| H8 分享链接 | — | app.js |
