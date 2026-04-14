# 拼课课程系统 Progress

Date: 2026-04-12
Status: Active
Owner: Hermes
Scope: 当前仓库原型实现追踪

---

## 当前状态

| Item | Status | Notes |
|---|---|---|
| Batch 1 Python 后端原型落点确认 | Done | 用户确认在当前仓库新建原型 |
| Contract freeze 文档 | Done | 已补齐最小冻结版本 |
| Progress 文档 | Done | 当前文件 |
| Batch 1 原型测试编写 | Done | 已覆盖契约基线、模型约束、创建/更新/详情/列表，并新增 schema / index / 约束表达测试；SQLite repository 闭环测试已补齐，当前 `tests/group_class_backend` 全量通过（25 passed） |
| Batch 1 原型实现 | Done | 已完成 B1-F01、B1-F02、B1-F03、B1-F04、B1-F05、B1-F06、B1-F07、B1-F08 最小闭环；当前已将 SQLite schema 接入 `SQLiteClassRepository`，形成 create/update/detail/list 可运行持久化闭环 |
| Batch 2 提交审核最小闭环 | Done | 已完成 B2-TC-003 最小实现：`submit_class_review` 支持 `DRAFT/REJECTED -> PENDING_REVIEW`，补齐内存/SQLite 测试闭环；最新回归 `tests/group_class_backend` 全量通过（29 passed in 0.49s） |
| Batch 2 审核通过最小闭环 | Done | 已完成 B2-TC-004 最小实现：`approve_class_review` 支持 `PENDING_REVIEW -> OPEN_FOR_ENROLLMENT`，补齐非法状态/版本冲突/SQLite 持久化测试闭环；最新回归 `tests/group_class_backend` 全量通过（33 passed in 0.50s） |
| Batch 2 最小权限强校验 | Done | 已完成 B2-TC-002 最小实现：`INITIATOR` 仅可编辑/提交自己创建的课程，`approve/reject` 必须显式携带 `CLASS_ADMIN`/`SUPER_ADMIN` 角色；补齐 creator/reviewer 持久化与 schema 测试，最新回归 `tests/group_class_backend` 全量通过（44 passed in 0.51s） |
| Batch 2 前台可见性过滤 | Done | 已完成 B2-TC-006 最小实现：`get_class_detail(public_only=True)` 与 `list_classes(public_only=True)` 仅暴露 `OPEN_FOR_ENROLLMENT` 课程，补齐内存/SQLite 可见性过滤测试；最新回归 `tests/group_class_backend` 全量通过（50 passed in 0.53s） |
| Batch 3 前台列表/详情展示增强 | Done | 已完成 B3-TC-001 ~ B3-TC-005 最小原型：前台列表/详情支持公开可见状态集（`OPEN_FOR_ENROLLMENT` / `ALMOST_CONFIRMED` / `CONFIRMED` / `FULL` / `WAITLIST_OPEN` / `IN_PROGRESS`），返回状态标签、差额人数文案、剩余名额、主 CTA 与候补可用性字段；最新回归 `tests/group_class_backend` 全量通过（52 passed in 0.53s） |
| Batch 3 详情页决策信息 / 规则 / FAQ 内容建模 | Done | 已完成 B3-TC-005 最小后端闭环：课程草稿创建/更新/前台详情接口支持 `courseSubtitle`、适合/不适合人群、课程目标、课时与排课摘要、成班/请假/候补/不成班规则、FAQ 摘要等字段，并完成 SQLite 持久化、详情回显与 `sessionCount > 0` 校验；最新回归 `tests/group_class_backend` 全量通过（55 passed in 0.54s） |
| Batch 4 报名 / 候补最小后端闭环 | Done | 已完成 B4-TC-001 / B4-TC-003 / B4-TC-007 最小实现：新增 `submit_registration`、报名/候补字段校验、课程人数/候补计数更新、报名审计写入与 SQLite 持久化闭环；最新 targeted 验证 `tests/group_class_backend/models/test_models.py tests/group_class_backend/persistence/test_schema_definition.py tests/group_class_backend/registrations/test_registration_commands.py -q` 通过（22 passed in 0.52s），当前 `tests/group_class_backend` 全量通过（66 passed in 0.56s） |
| Batch 4 后台报名列表/权限过滤 | Done | 已完成 B4-TC-005 最小实现：新增 `list_registrations` 后台列表查询，支持 `CLASS_ADMIN` / `SUPER_ADMIN` 查看全部报名、`INITIATOR` 仅查看自己创建课程的报名记录，并补齐内存/SQLite 过滤测试；最新 targeted 验证 `tests/group_class_backend/registrations/test_registration_commands.py -q` 通过（9 passed in 0.45s），当前 `tests/group_class_backend` 全量通过（69 passed in 0.59s） |
| Batch 4 报名详情/备注最小后端闭环 | Done | 已完成 B4-TC-006 最小实现：新增 `get_registration_detail` 与 `update_registration_notes`，支持后台报名详情回显、跟进备注更新、资源归属过滤与 SQLite 持久化闭环；最新 targeted 验证 `tests/group_class_backend/registrations/test_registration_commands.py -q` 通过（12 passed in 0.47s），当前 `tests/group_class_backend` 全量通过（72 passed in 0.60s） |
| Batch 4 报名状态管理最小后端闭环 | Done | 已完成 B4-TC-008 最小实现：新增 `update_registration_status`，支持后台标记 `VALID` / `INVALID` / `CANCELLED` 并回显最新状态，沿用 `CLASS_ADMIN` / `SUPER_ADMIN` / `INITIATOR` + 课程创建人资源归属过滤，补齐 in-memory / SQLite 测试；最新 targeted 验证 `tests/group_class_backend/registrations/test_registration_commands.py -q` 通过（15 passed in 0.47s），当前 `tests/group_class_backend` 全量通过（79 passed in 0.58s） |
| Batch 4 试听申请最小后端闭环 | Done | 已补齐 `submit_registration` 的 `TRIAL` 路径回归，验证试听申请成功响应、`wantsTrial` 持久化以及不会误增 `current_students` / `waitlist_count`；最新 targeted 验证 `tests/group_class_backend/registrations/test_registration_commands.py -q` 通过（17 passed in 0.49s），当前 `tests/group_class_backend` 全量通过（81 passed in 0.60s） |
| Batch 5 从模板创建课程最小后端闭环 | Done | 已完成 B5-TC-003 + B5-TC-004 最小实现：`create_class_draft` 仅允许使用存在且启用中的模板创建课程，且会对 `className`、`classType`、价格、人数、课程说明/规则/FAQ 等字段执行模板默认值自动回填；显式 payload 优先于模板默认值，`None`/空字符串会触发回填，并补齐 in-memory / SQLite 测试保护；最新 targeted 验证 `tests/group_class_backend/classes/test_create_class_draft.py tests/group_class_backend/classes/test_class_queries_and_update.py -q` 通过（46 passed in 0.51s），当前 `tests/group_class_backend` 全量通过（85 passed in 0.62s） |

---

## 执行记录

### 2026-04-12
1. 确认当前仓库无现成拼课业务代码。
2. 用户选择在当前仓库中新建 Batch 1 Python 后端原型。
3. 已补齐最小 `contract freeze` 文档与 progress 文档。
4. 已按 TDD 落地课程草稿创建能力与基础模型约束测试。
5. 已新增课程草稿更新、课程详情、后台课程列表测试，并实现最小控制器/仓储闭环。
6. 已完成 targeted verification：`python -m pytest tests/group_class_backend -q` → `24 passed`.
7. 已新增 `apps/group_class_backend/persistence/schema.py`，补齐 `classes` / `registrations` / `class_templates` 的 SQLite schema、索引与约束表达。
8. 已新增 `tests/group_class_backend/persistence/test_schema_definition.py`，验证核心表、索引与关键 Batch 1 约束。
9. 已新增 `apps/group_class_backend/classes/repository.py` 中的 `SQLiteClassRepository`，将 schema 表达接入 classes create/update/detail/list 的持久化闭环。
10. 已新增 SQLite repository 闭环测试，并完成 targeted verification：`python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py::test_sqlite_repository_supports_create_update_detail_and_list_flow -q` → `1 passed`。
11. 已完成 Batch 1 当前原型全量验证：`python -m pytest tests/group_class_backend -q` → `25 passed`。
12. 已补充本轮 Batch 1 自测/验收记录，当前仓库内的 Batch 1 Python 后端原型可判定为完成；真实 migration framework 仍可作为后续工程化增强项独立推进。
13. 复核 Batch 1 全量验证：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `25 passed in 0.50s`，确认当前代码、测试、文档状态一致，可作为 Batch 1 退出验收的最终证据。
14. 已按 TDD 补齐 Batch 2 最小后端能力 `submit_class_review`，完成 `DRAFT/REJECTED -> PENDING_REVIEW` 状态流转、版本冲突与非法状态保护。
15. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `10 passed in 0.44s`。
16. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `29 passed in 0.51s`。
17. 已完成 Batch 2 文档同步，补充提交审核自测/验收记录，并更新 progress / issue log。
18. 复核 targeted 验证：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `10 passed in 0.54s`。
19. 复核全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `29 passed in 0.49s`。
20. 已按 TDD 为 Batch 2 审核通过最小闭环先补失败测试，新增 `approve_class_review` 的成功流转、非法状态、版本冲突与 SQLite 持久化测试，并先验证 RED（导入失败）。
21. 已实现 `approve_class_review` 最小控制器逻辑，支持 `PENDING_REVIEW -> OPEN_FOR_ENROLLMENT`，保留统一错误码、版本并发保护、审计事件与动作字段契约。
22. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `14 passed in 0.46s`。
23. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `33 passed in 0.63s`。
24. 已补充 Batch 2 审核通过自测/验收记录，并同步更新 progress / issue log，当前可进入 Batch 2 下一最小功能点（审核驳回或权限强校验）的 TDD 循环。
25. 已按 TDD 为 Batch 2 审核驳回最小闭环先补失败测试，新增 `reject_class_review` 的成功流转、非法状态、版本冲突与 SQLite 持久化测试，并先验证 RED（导入失败）。
26. 已实现 `reject_class_review` 最小控制器逻辑，支持 `PENDING_REVIEW -> REJECTED`，保留统一错误码、版本并发保护、审计事件与动作字段契约。
27. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `18 passed in 0.46s`。
28. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `37 passed in 0.51s`。
29. 已补充 Batch 2 审核驳回自测/验收记录，并同步更新 progress / issue log，当前可进入 Batch 2 下一最小功能点（角色/资源级权限强校验）的 TDD 循环。
30. 已按 TDD 补齐 Batch 2 最小权限强校验，新增 `INITIATOR` 资源归属限制、审核动作显式管理员角色门禁、`creator_id` / `reviewer_id` 持久化字段与对应 SQLite schema 表达。
31. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `24 passed in 0.43s`。
32. 已修正 schema 约束测试以匹配 `creator_id` 非空持久化要求，并完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `44 passed in 0.51s`。
33. 已补充 Batch 2 最小权限强校验自测/验收记录，并同步更新 progress / issue log；当前 Batch 2 最小权限门禁已落地，后续可继续推进前台可见性过滤或更完整权限抽象。
34. 已按 TDD 为 Batch 2 前台可见性过滤先补失败测试，新增 `get_class_detail(public_only=True)` 与 SQLite 对应场景下的不可见/可见课程过滤断言，并先验证 RED（`get_class_detail` 缺少 `public_only` 入参）。
35. 已实现 `get_class_detail(public_only=True)` 最小可见性过滤逻辑，与既有 `list_classes(public_only=True)` 保持一致，仅向前台暴露 `OPEN_FOR_ENROLLMENT` 课程。
36. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `31 passed in 0.49s`。
37. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `50 passed in 0.53s`。
38. 已补充 Batch 2 前台可见性过滤自测/验收记录，并同步更新 progress / issue log；当前原型已具备 Batch 2 最小前台可见状态过滤基线，可继续推进 Batch 3 前台列表/详情接口实现。
39. 已按 TDD 为 Batch 3 前台列表/详情增强补齐失败测试，新增 `ALMOST_CONFIRMED` / `FULL` 等前台展示场景的状态标签、差额人数文案、剩余名额、主 CTA 与候补可用性断言。
40. 已实现前台课程列表/详情最小展示映射：`public_only=True` 支持公开可见状态集（`OPEN_FOR_ENROLLMENT` / `ALMOST_CONFIRMED` / `CONFIRMED` / `FULL` / `WAITLIST_OPEN` / `IN_PROGRESS`），并返回 `statusLabel`、`progressText`、`remainingSeats`、`primaryAction`、`primaryActionLabel`、`isWaitlistAvailable` 等前台字段。
41. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `33 passed in 0.49s`。
42. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `52 passed in 0.53s`。
43. 已补充 Batch 3 前台列表/详情增强自测/验收记录，并同步更新 progress / issue log；当前原型已具备 Batch 3 最小前台课程卡片/详情展示字段基线，可继续推进详情页决策信息、规则与 FAQ 内容建模。
44. 已按 TDD 为 Batch 3 详情页决策信息/规则/FAQ 内容建模补齐失败测试，新增前台详情字段回显、SQLite 持久化回读与课程草稿更新断言。
45. 已为 `GroupClass`、控制器与 `SQLiteClassRepository` 扩展 `courseSubtitle`、`targetAudience`、`unsuitableAudience`、`courseGoal`、`scheduleSummary`、`sessionCount`、`groupRule`、`absenceRule`、`waitlistRule`、`failureRule`、`faqSummary` 字段，并将其接入创建、更新、后台序列化与前台详情返回。
46. 已补充 `sessionCount > 0` 领域校验与错误返回断言，保证详情页课时信息具有最小有效约束。
47. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `36 passed in 0.57s`。
48. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `55 passed in 0.54s`。
49. 已补充 Batch 3 详情页内容建模自测/验收记录，并同步更新 progress / issue log；当前原型已具备 Batch 3 对“决策信息、规则、FAQ、CTA 完整”的最小后端契约基线，下一步可进入 Batch 4 报名/候补闭环。
50. 已按 TDD 为 Batch 4 报名/候补最小后端闭环先补测试，新增报名成功、候补成功、未知课程/非法状态拦截与 SQLite 持久化断言，并先修正测试中的 dataclass 状态更新写法。
51. 已实现 `Registration` 扩展字段模型、`submit_registration` 控制器与 `InMemory` / `SQLiteRegistrationRepository`，支持 `ENROLLMENT` / `WAITLIST` 提交、必填字段校验、课程人数/候补计数更新、审计事件记录与标准成功/错误响应。
52. 已扩展 SQLite `registrations` schema，补齐 `parent_name`、`contact_info`、`student_name`、`student_grade`、`english_level`、布尔偏好字段、备注字段以及 `created_at` / `updated_at` 持久化列，保证 Batch 4 字段与 Batch 1 建表基线兼容。
53. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/models/test_models.py tests/group_class_backend/persistence/test_schema_definition.py tests/group_class_backend/registrations/test_registration_commands.py -q` → `22 passed in 0.52s`。
54. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `66 passed in 0.56s`。
55. 已补充 Batch 4 报名/候补最小后端闭环自测/验收记录，并同步更新 progress / issue log；当前原型已具备前台报名/候补提交与课程人数联动的最小契约基线，下一步可继续推进后台报名管理列表、详情备注与资源归属过滤。
56. 已按 TDD 为 Batch 4 后台报名列表最小后端能力补齐测试，新增 `list_registrations` 在 `INITIATOR` 资源归属过滤、无后台角色拒绝访问以及 SQLite 过滤一致性断言。
57. 已实现 `list_registrations` 最小控制器逻辑，支持后台报名列表返回课程名、报名类型、联系方式、报名时间与备注字段，并按 `CLASS_ADMIN` / `SUPER_ADMIN` / `INITIATOR` 做后端权限与课程创建人范围过滤。
58. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q` → `9 passed in 0.45s`。
59. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `69 passed in 0.59s`。
60. 已补充 Batch 4 后台报名列表/权限过滤自测/验收记录，并同步更新 progress / issue log；当前原型已具备后台报名记录最小读取与资源归属过滤基线，下一步可继续推进报名详情/备注能力。
61. 已按 TDD 为 Batch 4 报名详情/备注能力补齐测试，新增 `get_registration_detail` 与 `update_registration_notes` 的成功路径、资源归属拒绝访问与 SQLite 持久化断言。
62. 已实现 `get_registration_detail` 与 `update_registration_notes` 最小控制器逻辑，支持后台报名详情回显、跟进备注更新、`CLASS_ADMIN` / `SUPER_ADMIN` / `INITIATOR` 角色访问控制与课程创建人资源归属过滤。
63. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q` → `12 passed in 0.67s`。
64. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `72 passed in 0.58s`。
65. 已补充 Batch 4 报名详情/备注最小闭环自测/验收记录，并同步更新 progress / issue log / ACPX 计划 / 架构执行更新；当前 Batch 4 最小后端闭环已覆盖报名提交、候补提交、后台报名列表、详情与备注能力，下一步可评估导出名单或更细粒度报名状态管理。
66. 已按 TDD 为 Batch 4 报名状态管理能力补齐测试，新增 `update_registration_status` 的成功路径、非法状态值校验、资源归属拒绝访问与 SQLite 持久化断言。
67. 已实现 `update_registration_status` 最小控制器逻辑，支持后台标记 `VALID` / `INVALID` / `CANCELLED` 并回显最新状态，沿用 `CLASS_ADMIN` / `SUPER_ADMIN` / `INITIATOR` 角色访问控制与课程创建人资源归属过滤。
68. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q` → `15 passed in 0.47s`。
69. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `79 passed in 0.58s`。
70. 已补充 Batch 4 报名状态管理最小闭环文档同步，当前 Batch 4 最小后端闭环已覆盖报名提交、候补提交、后台报名列表、详情、备注与状态管理能力；下一步可评估导出名单或更细粒度资源范围配置。
71. 已按 TDD 为 Batch 4 试听申请最小后端闭环补齐测试，新增 `TRIAL` 提交成功、课程人数/候补计数不变与 SQLite 持久化断言。
72. 已确认现有 `submit_registration` 满足试听申请最小契约：成功响应返回 `registerType=TRIAL`，并持久化 `wantsTrial`，同时不误增 `current_students` / `waitlist_count`。
73. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q` → `17 passed in 0.49s`。
74. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `81 passed in 0.60s`。
75. 已补充 Batch 4 试听申请最小闭环文档同步；当前 Batch 4 最小后端闭环已覆盖报名、候补、试听申请、后台报名列表、详情、备注与状态管理能力，下一步可优先评估导出报名名单能力。
76. 已按 TDD 为 Batch 5 从模板创建课程最小后端闭环补齐失败测试，新增模板不存在与模板停用场景断言，并复用现有 `InMemoryTemplateRepository` 作为模板依赖。
77. 已在 `create_class_draft` 增加模板启用态校验：缺失模板返回 `CLASS_NOT_FOUND`，停用模板返回 `VALIDATION_INVALID_ARGUMENT`，避免从停用模板继续建课。
78. 已完成 targeted verification：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `41 passed in 0.51s`。
79. 已完成当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `82 passed in 0.59s`。
80. 已补充 Batch 5 从模板创建课程最小闭环文档同步；当前 Batch 5 已具备“模板必须存在且启用”这一最小后端保护，下一步可继续推进模板字段自动回填、复制建课或模板管理写路径。
81. 已复核并同步最新 pytest 结果到 progress / issue log / architecture / ACPX plan / test-and-acceptance 文档，确保 Batch 5 验证快照与当前仓库真实回归结果一致（当前 full regression 为 `84 passed in 0.59s`）。
82. 已重新执行 Batch 5 相关 targeted 验证：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_create_class_draft.py tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `45 passed in 0.51s`，并再次执行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `84 passed in 0.59s`；已将最新验证命令与结果同步回 progress / issue log / ACPX plan / test-and-acceptance 文档，当前下一最小后端缺口仍为模板字段自动回填。
83. 本轮继续复核 Batch 5 相关 targeted/full pytest，确认当前回归基线已更新为 `45 passed in 0.51s` / `84 passed in 0.59s`，并同步修正文档中的旧快照，避免后续继续引用过期的 `41/43/82` 结果。
84. 已复核当前 `create_class_draft` 模板字段自动回填实现与测试覆盖：模板默认值现可回填 `className`、`classType`、价格、人数、课程说明/规则/FAQ 等字段，显式 payload 仍优先于模板默认值，`None`/空字符串会触发回填。
85. 已重新执行 Batch 5 相关 targeted 验证：`source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_create_class_draft.py tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `46 passed in 0.51s`。
86. 已重新执行当前原型全量验证回归：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `85 passed in 0.62s`。
87. 已将 Batch 5 文档同步到最新状态：当前从模板建课最小闭环已覆盖模板存在/启用态校验 + 字段自动回填，下一最小后端缺口切换为复制建课或模板管理写路径。
88. 已开始前端 UI 分步改造，当前按“小任务逐个完成 + 每步同步 progress + 每步自检验收”的方式推进。
89. 已完成前端小任务 #8「页面壳改造」：重构 `apps/group_class_frontend/index.html` 顶栏/导航/页面外壳，并在 `apps/group_class_frontend/css/styles.css` 增加首屏渐变背景、品牌区、sticky 导航与容器基线样式。
90. 已完成该步自检：启动临时前端静态服务并使用 Edge headless 打开 `http://127.0.0.1:35330/#/public/classes`，确认新页面壳结构、品牌文案、导航容器与内容区域正常渲染；当前未发现影响真实后端联调的结构性问题。
91. 已完成前端小任务 #9「视觉设计系统基线」：扩展 `apps/group_class_frontend/css/styles.css` 设计 token、阴影/圆角/间距体系、统一 panel/card 质感、按钮 hover/focus、输入框 focus、表格表头/行 hover 与基础响应式断点，为后续列表/详情/表单/后台页重排提供统一样式底座。
92. 已完成该步自检：继续使用临时前端静态服务与 Edge headless 打开 `http://127.0.0.1:35330/#/public/classes`，确认新样式文件已生效，页面壳、面板、按钮、状态标签与列表栅格正常渲染；同时通过 `curl -I http://127.0.0.1:35330/` 确认静态服务返回 `HTTP/1.0 200 OK`，当前未发现阻塞后续前台列表改造的样式层问题。
93. 已完成前端小任务 #10「前台课程列表重设计」：重构 `apps/group_class_frontend/js/app.js` 中 `renderPublicList`，新增看板 hero 摘要区、课程卡片头部状态区、剩余名额/价格/人数指标块、上课时间/开课周期/成班门槛信息块与更明确的主次 CTA；同步在 `apps/group_class_frontend/css/styles.css` 补齐 `list-hero`、`summary-pill`、`class-card`、`metric-tile`、`class-card-facts` 等样式与窄屏响应式适配。
94. 已完成该步自检：继续使用临时前端静态服务与 Edge headless 打开 `http://127.0.0.1:35330/#/public/classes`，确认前台列表新 hero 区、课程卡片层级、报名/候补 CTA、剩余名额与关键事实块均已渲染；同时复核 `curl -I http://127.0.0.1:35330/` 仍返回 `HTTP/1.0 200 OK`，当前未发现阻塞下一步详情页改造的问题。
95. 已完成前端小任务 #11「课程详情页重设计」：重构 `apps/group_class_frontend/js/app.js` 中 `renderPublicDetail`，新增详情 hero 区、课程状态/进度、剩余名额/价格/人数指标块、报名决策信息侧栏、适合/不适合对象与课程目标分区、规则说明 facts block；同步在 `apps/group_class_frontend/css/styles.css` 补齐 `detail-hero`、`detail-metrics`、`detail-side-card`、`detail-content-grid`、`detail-facts` 等样式与响应式布局。
96. 已完成该步自检：继续使用临时前端静态服务与 Edge headless 打开 `http://127.0.0.1:35330/#/public/classes/cls-dcf042ed5957`，确认详情页新 hero 区、报名侧栏、指标块、适合对象与规则说明区均已渲染；同时复核 `curl -I http://127.0.0.1:35330/` 仍返回 `HTTP/1.0 200 OK`，当前未发现阻塞下一步报名表单改造的问题。
97. 已完成前端小任务 #12「报名表单重设计」：重构 `apps/group_class_frontend/js/app.js` 中 `formTemplate`，新增报名 hero 区、提交流程说明侧栏、家长信息/学员信息/补充说明三段式表单分组、双列表单栅格、必填标识、占位提示与提交确认栏；同步在 `apps/group_class_frontend/css/styles.css` 补齐 `enrollment-shell`、`enrollment-hero`、`form-section`、`form-grid`、`required-mark`、`form-submit-bar` 等样式与移动端适配。
98. 已完成该步自检：继续使用临时前端静态服务与 Edge headless 打开 `http://127.0.0.1:35330/#/public/enroll/cls-dcf042ed5957?type=ENROLLMENT`，确认报名页新 hero 区、流程说明、分组表单、必填标识与提交栏均已渲染；同时复核 `curl -I http://127.0.0.1:35330/` 仍返回 `HTTP/1.0 200 OK`，当前未发现阻塞下一步后台课程列表改造的问题。
99. 已完成前端小任务 #13「后台课程列表重设计」：重构 `apps/group_class_frontend/js/app.js` 中 `renderAdminClasses`，新增后台 hero 摘要区、课程总数 summary pill、运营视图头部、课程名称 + ID 组合单元格、动作 tags 与表格横向滚动容器；同步在 `apps/group_class_frontend/css/styles.css` 补齐 `admin-hero`、`admin-summary-grid`、`admin-table-panel`、`table-wrap`、`admin-course-cell`、`action-tags`、`action-tag` 等样式与响应式适配。
100. 已完成该步自检：继续使用临时前端静态服务与 Edge headless 打开 `http://127.0.0.1:35330/#/admin/classes`，确认后台 hero 区、summary pill、增强表格、动作标签与课程 ID 展示均已渲染；同时复核 `curl -I http://127.0.0.1:35330/` 仍返回 `HTTP/1.0 200 OK`，当前未发现阻塞下一步响应式/状态细节收尾的问题。
101. 已完成前端小任务 #14「响应式与状态细节收尾」：在 `apps/group_class_frontend/js/app.js` 增加导航激活态同步与轻量 loading 状态面板，并在 `apps/group_class_frontend/css/styles.css` 补齐 `nav-link.is-active`、`loading-panel`、spinner 动画、窄屏按钮满宽与多页面响应式收尾规则，统一前台/详情/报名/后台页的交互状态反馈。
102. 已完成该步自检：继续使用临时前端静态服务与 Edge headless 分别打开 `http://127.0.0.1:35330/#/public/classes` 与 `http://127.0.0.1:35330/#/admin/classes`，确认导航激活态会随路由切换，公共看板与后台列表均正常渲染；同时复核 `curl -I http://127.0.0.1:35330/` 仍返回 `HTTP/1.0 200 OK`，当前可进入最终 UI 联调验收。
103. 已完成前端小任务 #16「后台课程详情页补齐」：为后端补齐 `GET /api/v1/admin/classes/{classId}` 读取路由，并在 `apps/group_class_frontend/js/api.js` 新增 `getAdminClassDetail`，同时重构 `apps/group_class_frontend/js/app.js` 增加后台课程详情页 hero、运营摘要指标、适配/目标侧栏、规则与 FAQ 分区，并将后台列表“查看”入口切换到 `#/admin/classes/:id`。
104. 已同步在 `apps/group_class_frontend/css/styles.css` 补齐 `admin-detail-hero`、`admin-detail-summary`、`admin-detail-grid`、`admin-metric-grid`、`admin-detail-facts` 等样式与窄屏响应式规则；已完成该步自检：重启 `8000` 端口真实后端后复核 `GET /api/v1/admin/classes` 与 `GET /api/v1/admin/classes/{classId}` 均返回 200，后台详情所需字段完整；同时校验前端静态壳 `index.html` 仍正常加载 `css/styles.css` 与 `js/app.js`，并完成 `app.js` / `server.py` 语法检查通过。受当前本机 Edge sandbox 权限限制，`--dump-dom` 浏览器级 DOM 导出仍报 executable access denied，但接口与路由链路联调已闭环，当前可判定前端小任务 #16 完成。
