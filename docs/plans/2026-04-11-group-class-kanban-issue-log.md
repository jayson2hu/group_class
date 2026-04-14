# 拼课课程系统 Batch 0 Issue Log

Date: 2026-04-11  
Status: Active  
Role: PM / Delivery Manager  
Owner: Hermes  
Suggested Path: `docs/plans/2026-04-11-group-class-kanban-issue-log.md`

Depends on:
- `docs/plans/2026-04-11-group-class-kanban-prd.md`
- `docs/plans/2026-04-11-group-class-kanban-delivery-governance.md`
- `docs/plans/2026-04-11-group-class-kanban-ui-design.md`
- `docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
- `docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
- `docs/plans/2026-04-11-group-class-kanban-acpx-implementation-plan.md`

---

## 1. 目的

本文件用于作为拼课课程系统在 Batch 0 至后续各 Batch 的统一问题清单、风险日志与升级追踪入口。

目标：
1. 对需求冲突、设计冲突、技术阻塞、测试失败、验收不通过、延期风险、依赖风险进行统一登记。
2. 保证问题“发现即记录、变化即更新、关闭可追溯”。
3. 为 Hermes 的设计审批、功能点审批、Batch 审批提供依据。
4. 作为 Batch 0 退出评审与 Batch 1 准入判断的正式输入。

---

## 2. 使用规则

1. 所有影响范围、契约冻结、权限边界、状态流转、批次准入的问题，必须进入本日志。
2. 每条 issue 必须有唯一 `Issue ID`、唯一 `DRI`、明确下一步动作、目标日期。
3. issue 状态变化时必须同步更新，不允许只在口头或聊天中处理。
4. 关闭 issue 前必须补充解决说明、验证结果、证据链接或文档引用。
5. 跨文档冲突优先登记为 issue，再推动改文档，不允许跳过记录直接“默默修正”。
6. 未完成分级、未指定负责人、未写下一步的 issue，视为无效 issue，不计入治理闭环。
7. Batch 结束前必须复核所有未关闭 issue，并给出处理意见：关闭、延期、接受风险、升级处理。
8. 与审批门禁直接相关的问题，必须标记 `Exit Gate Relation`。

---

## 3. 严重度定义

| 等级 | 定义 | 处理要求 |
|---|---|---|
| `S0-Critical` | 阻断 Batch 准入、核心契约无法冻结、关键角色/状态/权限口径冲突，无法继续推进 | 立即升级，24 小时内形成结论 |
| `S1-High` | 不阻断当天工作，但会直接导致返工、错误实现、验收失败或跨团队并行失效 | 当前 Batch 内必须处理 |
| `S2-Medium` | 有明确风险，但可在后续指定 Batch 前关闭，不立即阻断当前批次 | 必须指定处理批次和 owner |
| `S3-Low` | 优化项、补充项、观察项，对当前交付无直接阻断 | 可延后，但不得丢失记录 |

---

## 4. 优先级定义

| 优先级 | 定义 | 预期动作 |
|---|---|---|
| `P0` | 不解决则不能通过当前门禁 | 立即排队处理 |
| `P1` | 当前批次内高优先处理 | 本批次完成 |
| `P2` | 下一相关批次前处理 | 纳入计划并跟踪 |
| `P3` | 可观察或延期 | 保留日志，定期复盘 |

---

## 5. 状态定义

对齐治理文档，统一使用以下 issue 状态：

| 状态 | 定义 |
|---|---|
| `Open` | 已发现，待分析或待分派 |
| `Investigating` | 已确认，正在分析根因或冻结口径 |
| `Resolved` | 已完成修复/方案明确，待验证关闭 |
| `Closed` | 已验证通过，正式关闭 |
| `Deferred` | 明确延期处理，已接受风险并指定后续批次 |

补充规则：
1. `Resolved` 不等于 `Closed`，必须经过复核或验收。
2. `Deferred` 必须写明延期原因、目标批次、接受人。
3. 批次退出评审时，所有 `Open` / `Investigating` issue 必须逐条解释是否允许带入下一阶段。

---

## 6. Ownership 规则

1. 每条 issue 必须指定一个 `DRI`，只允许一个主负责人。
2. `PM / Delivery Manager` 负责维护 issue log 的完整性、分级、节奏与升级。
3. `Product` 负责需求范围、优先级、业务口径类问题。
4. `Designer` 负责页面结构、交互、状态展示、字段表达类问题。
5. `Architect` 负责数据模型、接口契约、状态机、权限模型、非功能基线类问题。
6. `Frontend / Backend` 负责实现偏差、技术阻塞、联调问题。
7. `QA / Hermes` 负责验证关闭、门禁判断、是否允许带风险进入下一阶段。
8. 跨角色 issue 由 PM 指定主 DRI，其他角色作为 `Support Owners` 协作，不允许“共同负责”代替明确 owner。

---

## 7. Issue 字段 Schema

每条 issue 至少包含以下字段：

| 字段 | 必填 | 说明 |
|---|---|---|
| `Issue ID` | 是 | 唯一编号，建议 `B0-ISS-001` 格式 |
| `Date Opened` | 是 | 首次记录日期 |
| `Batch` | 是 | 所属批次，如 `Batch 0` |
| `Category` | 是 | 需求 / 设计 / 架构 / 测试 / 依赖 / 风险 / 治理 |
| `Title` | 是 | 一句话问题标题 |
| `Description` | 是 | 具体问题描述 |
| `Source Docs` | 是 | 来源文档或章节 |
| `Impact` | 是 | 对范围、进度、质量、并行开发、验收的影响 |
| `Severity` | 是 | `S0`~`S3` |
| `Priority` | 是 | `P0`~`P3` |
| `Status` | 是 | `Open` / `Investigating` / `Resolved` / `Closed` / `Deferred` |
| `DRI` | 是 | 主负责人 |
| `Support Owners` | 否 | 协作角色 |
| `Next Action` | 是 | 下一步动作 |
| `Target Date` | 是 | 计划完成日期 |
| `Escalation Needed` | 是 | `Yes` / `No` |
| `Exit Gate Relation` | 是 | 是否阻断 Batch 0 退出 / Batch 1 准入 |
| `Resolution Summary` | 否 | 解决摘要 |
| `Verification` | 否 | 验证结论与证据 |

---

## 8. 更新节奏

1. 发现问题后即时登记，当天不得跨日漏记。
2. 每次设计评审结束后，必须同步更新本日志。
3. 每次状态变化、owner 变化、目标日期变化，必须当次更新。
4. Batch 进行中至少每日一次由 PM / Delivery Manager 做状态巡检。
5. Batch 退出评审前，必须完成一次全量复核。
6. Hermes 进行阶段审批前，以本日志最新版本为准，不接受口头状态。

---

## 9. 升级规则

1. `S0/P0` issue：立即升级至 Hermes + Product + Architect，当日形成处理结论。
2. 涉及跨文档冲突且影响契约冻结的问题：直接升级为设计评审议题，不允许开发团队自行假设。
3. 连续 2 个工作日无更新的 `S1` issue：由 PM 主动升级。
4. 目标日期将延误且影响 Batch 退出时间的 issue：必须在延误前升级。
5. `Deferred` issue 若影响下一 Batch 准入，必须在下一 Batch 启动前重新打开或确认接受风险。
6. 任何影响权限、状态机、API 契约、前后台可见性的问题，默认需要 Hermes 知情。

---

## 10. 与 Batch 0 Exit Gate 的关系

对齐测试与验收文档，Batch 0 退出前必须满足：
1. UI 设计文档完成。
2. 架构设计文档完成。
3. 测试与验收文档完成。
4. issue log 已初始化。
5. progress 文档已初始化。
6. 角色权限边界已冻结。
7. 状态机已冻结。
8. API / 数据契约关键项已冻结。
9. Batch 1 测试基线已明确。
10. Hermes 已完成设计评审并给出结论。

因此，本日志中的 issue 分为三类：
- `Gate Blocker`：不关闭不得退出 Batch 0。
- `Next-Batch Blocker`：可结束 Batch 0，但不得进入相关下一批次。
- `Track Only`：记录并跟踪，不阻断当前退出。

---

## 11. 初始已知问题与风险种子清单

### 11.1 Active Issues

| Issue ID | Date Opened | Batch | Category | Title | Description | Source Docs | Impact | Severity | Priority | Status | DRI | Support Owners | Next Action | Target Date | Escalation Needed | Exit Gate Relation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `B0-ISS-001` | 2026-04-11 | Batch 0 | 治理 | `progress` 文档尚未初始化 | QA 文档与治理文档要求 Batch 0 必须补齐 `progress` 文档，但当前计划目录中尚不存在该文件。 | `test-and-acceptance` 15.1, 16.2；`delivery-governance` 4, 5；`acpx-implementation-plan` 5.2 | 阻断 Batch 0 退出与 Batch 1 准入 | `S0-Critical` | `P0` | `Open` | PM / Delivery Manager | QA, Hermes | 初始化 `docs/plans/2026-04-11-group-class-kanban-progress.md` 并补齐状态字段 | 2026-04-11 | Yes | `Gate Blocker` |
| `B0-ISS-002` | 2026-04-11 | Batch 0 | 设计/契约 | UI 字段与数据模型缺少一一映射清单 | 已有页面字段与数据模型字段，但尚未形成字段映射表，QA 明确将其列为 Batch 1 前的建议与风险。 | `test-and-acceptance` R-001, 16.2；`ui-design` 6.x；`architecture-design` 11 | 前后端并行开发存在返工风险，影响 Batch 1 实施 | `S1-High` | `P0` | `Open` | Architect | Designer, Frontend, Backend, QA | 输出字段映射表，覆盖列表页、详情页、表单页、后台创建页 | 2026-04-12 | Yes | `Gate Blocker` |
| `B0-ISS-003` | 2026-04-11 | Batch 0 | 需求/设计/架构 | “审核通过”与“发布”是否为同一步未冻结 | PRD、UI、架构、测试文档中同时存在“审核通过”和“发布”动作，但是否审核通过即发布、还是审核通过后需单独发布，当前口径未统一。 | `prd` 7.7；`ui-design` 6.6, 6.7；`architecture-design` 9.3, 10.4, 21.1；`test-and-acceptance` R-004 | 会直接影响状态机、按钮文案、接口设计与权限校验 | `S0-Critical` | `P0` | `Investigating` | Product | Architect, Designer, QA | 冻结业务口径并同步到状态机、页面动作、接口契约 | 2026-04-12 | Yes | `Gate Blocker` |
| `B0-ISS-004` | 2026-04-11 | Batch 0 | 权限 | `CLASS_ADMIN` 的审核/发布范围未产品化 | 文档多处提到“课程管理员可按配置审核/发布”，但默认范围、配置入口、资源边界尚未明确。 | `architecture-design` 9.3, 9.4, 21.1；`test-and-acceptance` 8.2, R-003 | Batch 2 权限实现和验收会产生争议，接口行为无法稳定 | `S1-High` | `P0` | `Open` | Product | Architect, QA | 定义默认策略、可配置范围及验收口径 | 2026-04-13 | Yes | `Next-Batch Blocker (Batch 2)` |
| `B0-ISS-005` | 2026-04-11 | Batch 0 | 状态机 | `ALMOST_CONFIRMED` 是展示态还是主状态仍有理解分歧 | PRD 将“即将成班”列为课程状态；架构与测试文档倾向其作为展示派生态，不替代主状态落库。 | `prd` 8.1, 8.3；`architecture-design` 10.4.2, 10.4.3；`test-and-acceptance` R-002, 9.2 | 状态实现、查询口径、标签展示和计数逻辑可能不一致 | `S1-High` | `P0` | `Open` | Architect | Product, Designer, QA | 冻结存储策略、展示规则与 API 返回口径 | 2026-04-12 | Yes | `Gate Blocker` |
| `B0-ISS-006` | 2026-04-11 | Batch 0 | 范围/设计 | 模板能力范围在 P0 与 Batch 5 之间存在冲突 | PRD 将“模板创建能力（基础版）”列为本期范围，架构文档仅在 P0 定义数据结构与引用关系，UI 设计将模板管理页放到 Batch 5，执行计划也将模板能力放到 Batch 5。 | `prd` 5.1, 7.8；`ui-design` 3.2；`architecture-design` 7.5, 2.3；`acpx-implementation-plan` 10 | 模板相关范围与批次边界不清，会导致验收口径不一致 | `S1-High` | `P1` | `Open` | Product | Architect, Designer, QA | 明确“P0 基础版”具体含义，并同步批次边界 | 2026-04-13 | Yes | `Gate Blocker` |
| `B0-ISS-007` | 2026-04-11 | Batch 0 | 范围 | “复制创建”能力归属批次不一致 | PRD 后台列表支持操作中包含“复制创建”，但执行计划将其放在 Batch 5，当前 UI/架构设计也未作为 Batch 1-4 必交付项。 | `prd` 7.5, 15；`acpx-implementation-plan` 10 | 影响后台操作范围和验收边界，易形成“做了/没做”争议 | `S2-Medium` | `P1` | `Open` | Product | PM, Designer, Architect | 明确是否移出本轮 MVP，或保留为后续增强项 | 2026-04-13 | No | `Gate Blocker` |
| `B0-ISS-008` | 2026-04-11 | Batch 0 | 数据一致性 | 报名成功后人数快照与课程状态更新规则未明确到实现细节 | 测试文档已识别该风险，但当前尚未明确报名落库后 `current_students`、`waitlist_count`、课程状态如何更新及何时更新。 | `test-and-acceptance` R-005；`prd` 6.2, 14.1；`architecture-design` 4.4, 6.2, 11.2 | Batch 4 容易出现人数、状态、前台展示不一致 | `S1-High` | `P1` | `Open` | Architect | Backend, QA, Product | 在 Batch 4 前补充状态与计数更新规则 | 2026-04-18 | No | `Next-Batch Blocker (Batch 4)` |
| `B0-ISS-009` | 2026-04-11 | Batch 0 | 需求/安全 | 报名是否要求登录、是否需要防刷未明确 | 架构文档提出普通用户是否要求登录为开放问题，当前前台公开查看已定，但报名提交口径、去重和防刷措施未冻结。 | `architecture-design` 9.2, 21.3, 21.4；`prd` 6.2, 7.3 | 影响 Batch 4 表单、风控字段、判重逻辑与用户体验 | `S2-Medium` | `P1` | `Open` | Product | Architect, QA | 冻结匿名留资/登录报名策略及最小防刷要求 | 2026-04-18 | No | `Next-Batch Blocker (Batch 4)` |
| `B0-ISS-010` | 2026-04-11 | Batch 0 | 状态机/审计 | `REJECTED` 是否作为显式数据库状态未最终定版 | 架构文档建议保留 `REJECTED` 以支持审计，但 PRD 更偏向“驳回后回草稿”的业务体验，需要统一数据态与展示态口径。 | `prd` 7.7；`architecture-design` 10.1, 21.2；`test-and-acceptance` 9.1 | 影响状态历史、列表过滤、前台可见性与验收口径 | `S1-High` | `P0` | `Open` | Architect | Product, QA | 明确数据层状态保留策略与前台/后台映射 | 2026-04-12 | Yes | `Gate Blocker` |
| `B0-ISS-011` | 2026-04-11 | Batch 0 | 范围 | 导出报名名单的交付批次未明确 | PRD、角色权限、后台操作中包含导出报名名单，但架构开放问题明确该项尚未确定是接口占位还是 Batch 4 必交付。 | `prd` 4.2, 7.5, 7.9；`architecture-design` 9.3, 21.8 | 影响后端接口、权限、Batch 4 范围与验收目标 | `S2-Medium` | `P2` | `Open` | Product | Architect, QA | 明确导出能力是本轮交付还是后续增强 | 2026-04-18 | No | `Track Only` |
| `B0-ISS-012` | 2026-04-11 | Batch 0 | 设计/体验 | `IN_PROGRESS` 前台是否展示及 CTA 行为未冻结 | UI 文档允许“进行中”前台展示，架构开放问题要求明确若展示则 CTA 是否关闭；PRD 候补表单又提到“进行中但允许登记下期意向”。 | `ui-design` 8.1；`architecture-design` 21.9；`prd` 7.4 | 影响前台状态展示、操作入口、候补/下期意向边界 | `S2-Medium` | `P1` | `Open` | Product | Designer, Architect, QA | 冻结进行中课程的前台展示与 CTA 规则 | 2026-04-18 | No | `Next-Batch Blocker (Batch 3/4)` |
| `B0-ISS-013` | 2026-04-11 | Batch 0 | 契约 | 错误返回规范尚未具象到接口清单级别 | 测试文档要求错误返回需可定位问题，但当前设计文档未给出统一错误结构、错误码或接口级示例。 | `test-and-acceptance` 10.1, 10.3, 15.1；`architecture-design` 1, 6, 19 | 会影响前后端并行开发、调试效率和验收一致性 | `S1-High` | `P0` | `Closed` | Architect | Backend, Frontend, QA | 已由冻结文档与当前原型统一成功/错误响应结构、关键错误码与接口返回示例；后续仅允许在冻结文档变更后调整。 | 2026-04-12 | Yes | `Gate Blocker` |
| `B1-ISS-001` | 2026-04-12 | Batch 1 | 实现/持久化 | Batch 1 当前仍为内存仓储原型，尚未落地关系型 schema / migration | 当前 `apps/group_class_backend/` 已完成内存态课程创建、更新、详情、列表最小闭环和基础模型，但 `classes` / `registrations` / `class_templates` 尚未具备真实数据库 schema、索引与 migration。 | `2026-04-12-group-class-kanban-batch1-python-backend-parallel-plan` 4.2, 5.1, 5.3, 6；当前原型代码 | 不阻断原型联调，但会阻断 Batch 1 对“关系型数据库 + schema 约束”目标的完全达成。 | `S1-High` | `P1` | `Closed` | Backend | Architect, QA, Hermes | 当前原型已完成 SQLite schema、索引、约束表达与 `SQLiteClassRepository` 接入，Batch 1 最小持久化闭环成立；若后续引入 Alembic / Django migrations，可作为工程化增强项单独跟踪。 | 2026-04-13 | No | `Next-Batch Blocker (Batch 1 completion)` |
| `B2-ISS-001` | 2026-04-12 | Batch 2 | 实现/状态流转 | Batch 2 审核通过最小闭环尚未实现 | Batch 2 测试基线要求支持 `PENDING_REVIEW -> OPEN_FOR_ENROLLMENT`，但在新增测试前控制器中尚不存在 `approve_class_review`，导致导入失败并阻断 B2-TC-004。 | `test-and-acceptance` 7.2, 9.1；`architecture-design` 7.3, 10.4；当前原型代码 | 阻断 Batch 2 审核通过能力、影响前台可见状态的后续实现基线。 | `S1-High` | `P1` | `Closed` | Backend | Architect, QA, Hermes | 已新增 `approve_class_review` 最小实现，完成成功流转、非法状态、版本冲突、SQLite 持久化测试闭环；当前以 `OPEN_FOR_ENROLLMENT` 作为审核通过落点继续与冻结设计保持一致。 | 2026-04-12 | No | `Next-Batch Blocker (Batch 2)` |
| `B2-ISS-002` | 2026-04-12 | Batch 2 | 实现/状态流转 | Batch 2 审核驳回最小闭环尚未实现 | Batch 2 当前仍缺少 `PENDING_REVIEW -> REJECTED` 的最小能力；在新增测试前控制器中不存在 `reject_class_review`，导致导入失败并阻断审核驳回闭环验证。 | `test-and-acceptance` 9.1；`architecture-design` 10.1, 21.2；当前原型代码 | 阻断 Batch 2 驳回返修路径，影响后续返修重提与状态历史口径验证。 | `S1-High` | `P1` | `Closed` | Backend | Architect, QA, Hermes | 已新增 `reject_class_review` 最小实现，完成成功流转、非法状态、版本冲突、SQLite 持久化测试闭环；当前以显式 `REJECTED` 状态承接驳回结果，与现有原型枚举和状态历史口径保持一致。 | 2026-04-12 | No | `Next-Batch Blocker (Batch 2)` |
| `B2-ISS-003` | 2026-04-12 | Batch 2 | 实现/权限 | Batch 2 最小资源级权限强校验尚未实现 | Batch 2 测试基线要求接口侧强校验资源归属与审核权限，但此前原型仅完成状态流转，尚未限制 `INITIATOR` 只能编辑/提交自己创建的课程，也未要求审核通过/驳回显式携带 `CLASS_ADMIN` / `SUPER_ADMIN` 角色上下文。 | `test-and-acceptance` 7.2, 8.2；`architecture-design` 9.3, 21.1；当前原型代码 | 会导致后端权限仅停留在前端显隐层，无法满足 Batch 2 对接口侧强校验的最小要求。 | `S1-High` | `P1` | `Closed` | Backend | Architect, QA, Hermes | 已新增最小权限门禁：`INITIATOR` 仅可编辑/提交自己创建的课程，审核通过/驳回仅允许 `CLASS_ADMIN` / `SUPER_ADMIN`，并要求显式 `actor_roles` 上下文；同时补齐 `creator_id` / `reviewer_id` 持久化与 schema 测试闭环。 | 2026-04-12 | No | `Next-Batch Blocker (Batch 2)` |
| `B2-ISS-004` | 2026-04-12 | Batch 2 | 实现/前台可见性 | Batch 2 前台可见性过滤尚未覆盖详情接口 | 当前原型已支持 `list_classes(public_only=True)` 过滤前台不可见状态，但 `get_class_detail()` 在新增测试前仍会直接返回 `DRAFT` / `PENDING_REVIEW` / `REJECTED` 课程详情，无法满足 B2-TC-006 对前台详情不可见的最小要求。 | `test-and-acceptance` 7.2, 9.2, 10.2；`architecture-design` 前后台可见性约束；当前原型代码 | 会导致前台详情接口泄露后台内部状态，破坏 Batch 2 与 Batch 3 的前台契约基线。 | `S1-High` | `P1` | `Closed` | Backend | Architect, QA, Hermes | 已为 `get_class_detail()` 增加 `public_only` 入参，并与 `list_classes(public_only=True)` 统一仅暴露 `OPEN_FOR_ENROLLMENT` 状态；同时补齐内存仓储与 SQLite 可见/不可见详情过滤测试。 | 2026-04-12 | No | `Next-Batch Blocker (Batch 2 / 3)` |
| `B3-ISS-001` | 2026-04-12 | Batch 3 | 实现/详情建模 | Batch 3 详情页缺少决策信息、规则与 FAQ 内容字段 | 当前原型已完成前台公开状态、标签、CTA 与人数文案返回，但在新增测试前，课程详情接口仍缺少 `courseSubtitle`、适合/不适合人群、课程目标、排课摘要、课时数、成班/请假/候补/不成班规则、FAQ 摘要等字段，无法满足 B3-TC-005 对“决策信息、规则、FAQ、CTA 完整”的最小要求。 | `test-and-acceptance` 7.3, B3-TC-005；`acpx-implementation-plan` 8.2, 8.5, 8.6；当前原型代码 | 会导致前台详情页无法提供用户决策所需的核心信息，也使 Batch 3 详情页验收口径无法闭环。 | `S1-High` | `P1` | `Closed` | Backend | Architect, QA, Hermes | 已为 `GroupClass`、控制器和 `SQLiteClassRepository` 增加详情内容字段，并将其接入创建/更新/详情序列化与 SQLite 持久化；同时新增 `sessionCount > 0` 校验与前台详情/SQLite 回归测试。 | 2026-04-12 | No | `Next-Batch Blocker (Batch 3)` |
| `B4-ISS-001` | 2026-04-12 | Batch 4 | 实现/报名闭环 | Batch 4 报名/候补最小后端闭环尚未实现 | 在新增测试前，原型仅有 `registrations` 基础表结构占位，尚无 `submit_registration` 控制器、报名仓储持久化、字段级校验、课程人数/候补计数联动与审计记录，阻断 B4-TC-001 / B4-TC-003 / B4-TC-007。 | `test-and-acceptance` 7.4, B4-TC-001, B4-TC-003, B4-TC-007；`acpx-implementation-plan` 9.2, 9.5, 9.6；当前原型代码 | 会导致前台无法完成报名/候补提交，也无法建立课程与报名数据一致性的最小验收基线。 | `S1-High` | `P1` | `Closed` | Backend | Architect, QA, Hermes | 已新增 `Registration` 扩展字段模型、`submit_registration` 控制器与内存/SQLite 报名仓储，支持 `ENROLLMENT` / `WAITLIST` / `TRIAL` 提交、必填校验、课程人数/候补计数更新、审计事件写入与标准成功/错误响应；同时补齐 SQLite schema 字段扩展与 targeted / full pytest 回归。 | 2026-04-12 | No | `Next-Batch Blocker (Batch 4)` |
| `B4-ISS-002` | 2026-04-12 | Batch 4 | 实现/试听申请验证 | Batch 4 试听申请路径缺少显式回归保护 | `submit_registration` 已支持 `TRIAL` 类型，但在新增测试前尚未显式验证试听申请成功响应、`wantsTrial` 持久化以及不会误增课程人数/候补计数，缺少 B4 试听申请最小验收证据。 | `test-and-acceptance` 7.4；当前原型代码 | 会导致试听申请路径虽存在实现却缺少稳定回归保护，后续修改可能破坏报名数据一致性而无法及时发现。 | `S1-High` | `P1` | `Closed` | Backend | QA, Hermes | 已新增 in-memory / SQLite 试听申请测试，验证 `TRIAL` 提交成功、`wantsTrial` 持久化以及 `current_students` / `waitlist_count` 保持不变；targeted / full pytest 均已通过，可作为试听申请最小闭环验收证据。 | 2026-04-12 | No | `Next-Batch Blocker (Batch 4)` |

### 11.2 初始风险摘要

| Risk ID | 风险描述 | 当前处理方式 |
|---|---|---|
| `R-PRD-001` | 课程状态更新不及时会降低用户信任 | 已转入 `B0-ISS-008` 跟踪 |
| `R-PRD-002` | 模板和审核机制缺失会导致课程供给混乱 | 模板范围走 `B0-ISS-006`，审核口径走 `B0-ISS-003/004` |
| `R-PRD-003` | 候补、调班、不成班规则不清晰易引发投诉 | 相关规则需在 Batch 3/4 前补充并纳入验收 |
| `R-QA-001` | issue/progress 若未持续维护会破坏治理门禁 | `progress` 初始化列入 `B0-ISS-001`，后续作为退出标准检查 |
| `R-QA-002` | 非功能项仅有基线、缺少量化指标 | 预发布前补量化指标，暂登记为后续跟踪项 |

---

## 12. 解决记录模板

```md
## Resolution Record

- Issue ID:
- Resolution Date:
- Resolved By:
- Resolution Type: Fix / Clarification / Scope Change / Defer
- Related Docs Updated:
- Related Code / PR / Commit:
- Summary:

### Root Cause
- 

### Decision / Fix
- 

### Impact Assessment
- Scope:
- Schedule:
- Test:
- Docs:

### Evidence
- 
- 

### Follow-up Actions
- 
```

---

## 13. 复核模板

```md
## Review Record

- Issue ID:
- Review Date:
- Reviewer:
- Review Type: Design / QA / Batch Exit / Hermes Approval

### Review Checklist
- Severity / Priority 是否仍然准确：
- 相关文档是否已同步：
- 影响范围是否已重新评估：
- 下一步是否清晰：
- 是否满足关闭条件：

### Review Decision
- Decision: Keep Open / Move to Investigating / Resolve / Close / Defer
- Comment:
- Reopen Criteria:
```

---

## 14. 关闭标准

issue 仅在满足以下条件后可关闭：
1. 问题口径已明确。
2. 相关文档已同步更新。
3. 若涉及实现，已完成最小验证或验收。
4. 影响方已知晓结论。
5. 已填写解决摘要与验证结论。
6. 若为延期项，已改为 `Deferred` 并指定目标批次，不得直接 `Closed`。

---

## 15. Batch 0 当前结论

截至 2026-04-11，本 issue log 已初始化，但 Batch 0 仍存在多个 `Gate Blocker`：
1. `progress` 文档未初始化。
2. 字段映射清单未补齐。
3. 审核通过与发布动作口径未冻结。
4. `ALMOST_CONFIRMED` 与 `REJECTED` 的状态口径未冻结。
5. 模板能力与复制创建的批次边界存在冲突。
6. 错误返回规范未具象到接口清单级别。

在上述 `Gate Blocker` 关闭前，不建议宣布 Batch 0 完成，也不建议进入 Batch 1 开发。

## 15.1 Batch 1 关闭补充记录

当前实现侧仅新增 `B1-ISS-001` 一项批次内问题，已在 2026-04-12 关闭，关闭依据为：
1. `apps/group_class_backend/persistence/schema.py` 已补齐 `classes`、`registrations`、`class_templates` 三张核心表及 Batch 1 所需索引/约束。
2. `apps/group_class_backend/classes/repository.py` 已新增 `SQLiteClassRepository`，完成 create/update/detail/list 的 SQLite 持久化闭环。
3. `tests/group_class_backend/persistence/test_schema_definition.py` 与 `tests/group_class_backend/classes/test_class_queries_and_update.py` 已覆盖 schema 约束与 SQLite repository 闭环。
4. 复核验证：`source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `25 passed in 0.50s`。

## Resolution Record

- Issue ID: `B1-ISS-001`
- Resolution Date: 2026-04-12
- Resolved By: Hermes
- Resolution Type: Fix
- Related Docs Updated:
  - `docs/plans/2026-04-11-group-class-kanban-progress.md`
  - `docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
  - `docs/plans/2026-04-11-group-class-kanban-issue-log.md`
- Related Code / PR / Commit:
  - `apps/group_class_backend/persistence/schema.py`
  - `apps/group_class_backend/classes/repository.py`
  - `tests/group_class_backend/persistence/test_schema_definition.py`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py`
- Summary:
  - Batch 1 原型已从仅内存仓储推进到 SQLite schema + repository 的最小关系型持久化闭环，满足当前批次对数据结构、索引与基础持久化能力的验收口径。

### Root Cause
- 初始 Batch 1 原型只完成内存态 create/update/detail/list，未提供关系型 schema、索引约束与真实持久化仓储实现，因此与并行开发计划中的 Batch 1 目标存在差距。

### Decision / Fix
- 新增 SQLite schema 定义与 `apply_schema()` 入口，显式落地 `classes` / `registrations` / `class_templates`。
- 新增 `SQLiteClassRepository`，保持与现有控制器契约兼容。
- 用测试锁定 schema 约束、索引存在性及 SQLite create/update/detail/list 闭环。

### Impact Assessment
- Scope: Batch 1 目标从“原型可跑”提升为“具备最小关系型持久化闭环”。
- Schedule: 不再阻断 Batch 1 关闭；真实 migration framework 留作后续工程化增强项。
- Test: `tests/group_class_backend` 全量通过，当前结果为 `29 passed in 0.51s`.
- Docs: progress / test-and-acceptance / issue log 已同步。

### Evidence
- `apps/group_class_backend/persistence/schema.py:1`
- `tests/group_class_backend/classes/test_class_queries_and_update.py:137`
- `tests/group_class_backend/persistence/test_schema_definition.py:15`
- `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `29 passed in 0.51s`

### Follow-up Actions
- 若后续项目从原型进入工程化阶段，可单独新开 issue 引入 Alembic / Django migrations，而不回退当前 Batch 1 已完成结论。

## Review Record

- Issue ID: `B1-ISS-001`
- Review Date: 2026-04-12
- Reviewer: Hermes
- Review Type: Batch Exit / Hermes Approval

### Review Checklist
- Severity / Priority 是否仍然准确：是，`S1/P1` 作为 Batch 1 关闭前问题是合理分级。
- 相关文档是否已同步：是。
- 影响范围是否已重新评估：是，当前仅保留“真实 migration framework 可后续增强”的工程化后续项。
- 下一步是否清晰：是，Batch 1 可关闭，后续按 Batch 2+ 计划推进。
- 是否满足关闭条件：是。

### Review Decision
- Decision: Close
- Comment: 当前仓库内的 Batch 1 Python 后端原型已满足计划文档与测试基线约束，可作为当前阶段完成依据。
- Reopen Criteria: 若后续发现 SQLite schema / repository 与冻结契约不一致，或 `tests/group_class_backend` 不再通过，则重新打开。

## 16. Batch 2 跟踪补充

### 16.1 Validation Snapshot
- Date: 2026-04-12
- Scope: `B2-TC-003` 提交审核最小闭环文档同步后复核
- Targeted Verification: `source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `10 passed in 0.54s`
- Full Regression: `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `29 passed in 0.49s`

### 16.2 Issue Status Decision
- New Blocking Issue: None
- Related Existing Issue: `B0-ISS-004` 仍保持 Open，继续作为后续 Batch 2 权限口径阻塞项。
- Comment: 当前 `submit_class_review` 最小闭环可以在不引入权限模型的前提下验收通过，因此不新增批次内阻断 issue，但后续审核通过/驳回功能点开始前必须先确认权限口径。

## 17. Batch 4 跟踪补充

### 17.1 Validation Snapshot
- Date: 2026-04-12
- Scope: `B4-TC-005` 后台报名列表/权限过滤最小闭环文档同步后复核
- Targeted Verification: `source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q` → `9 passed in 0.45s`
- Full Regression: `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `69 passed in 0.59s`

### 17.2 Issue Status Decision
- New Blocking Issue: None
- Closed Issue: `B4-ISS-001`
- Related Existing Issue: `B0-ISS-004` 保持 Open，继续跟踪更细粒度资源范围配置。
- Comment: 当前原型已为 Batch 4 后台报名管理补齐最小只读列表能力，并在后端执行角色 + 课程创建人资源归属过滤；Batch 4 后续剩余最小缺口收敛为报名详情/备注能力。

### 17.3 Validation Snapshot
- Date: 2026-04-12
- Scope: `B4-TC-006` 报名详情/备注最小闭环文档同步后复核
- Targeted Verification: `source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q` → `12 passed in 0.67s`
- Full Regression: `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `72 passed in 0.58s`

### 17.4 Issue Status Decision
- New Blocking Issue: None
- Closed Issue: `B4-ISS-001`
- Related Existing Issue: `B0-ISS-004` 保持 Open，继续跟踪 `CLASS_ADMIN` 更细粒度资源范围配置。
- Comment: 当前原型已为 Batch 4 后台报名管理补齐详情读取与备注更新最小写路径，且与后台列表保持一致的角色 + 课程创建人资源归属过滤；Batch 4 最小后端闭环已完成，后续可转入导出名单或更细粒度报名状态管理增强。

### 17.5 Validation Snapshot
- Date: 2026-04-12
- Scope: `B4-TC-008` 报名状态管理最小闭环文档同步后复核
- Targeted Verification: `source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q` → `15 passed in 0.47s`
- Full Regression: `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `79 passed in 0.58s`

### 17.6 Issue Status Decision
- New Blocking Issue: None
- Closed Issue: `B4-ISS-001`
- Related Existing Issue: `B0-ISS-004` 保持 Open，继续跟踪 `CLASS_ADMIN` 更细粒度资源范围配置。
- Comment: 当前原型已为 Batch 4 后台报名管理补齐报名状态更新最小写路径，支持 `VALID` / `INVALID` / `CANCELLED` 状态回显，并继续沿用角色 + 课程创建人资源归属过滤；后续增强重点仍为导出名单与更细粒度资源范围配置。

### 17.7 Validation Snapshot
- Date: 2026-04-12
- Scope: Batch 4 试听申请最小闭环文档同步后复核
- Targeted Verification: `source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q` → `17 passed in 0.49s`
- Full Regression: `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `81 passed in 0.60s`

### 17.8 Issue Status Decision
- New Blocking Issue: None
- Closed Issue: `B4-ISS-002`
- Related Existing Issue: `B0-ISS-004` 保持 Open，继续跟踪 `CLASS_ADMIN` 更细粒度资源范围配置。
- Comment: 当前原型已为 Batch 4 报名闭环补齐试听申请的显式回归保护，验证 `TRIAL` 提交成功、`wantsTrial` 持久化以及课程人数/候补计数不被误增；Batch 4 最小后端闭环现已覆盖报名、候补、试听申请、后台列表、详情、备注与状态管理能力，后续增强重点可优先转向导出名单。

## 18. Batch 5 跟踪补充

### 18.1 Validation Snapshot
- Date: 2026-04-12
- Scope: `B5-TC-003` / `B5-TC-004` 从模板创建课程 + 模板字段自动回填文档同步后复核
- Targeted Verification: `source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_create_class_draft.py tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `46 passed in 0.51s`
- Full Regression: `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `85 passed in 0.62s`

### 18.2 Issue Status Decision
- New Blocking Issue: None
- Closed Issue: None
- Related Existing Issue: `B0-ISS-005` 可继续保持 Open，用于跟踪 Batch 5 后续“复制创建 / 模板管理页”范围；`B0-ISS-004` 仍保持 Open，继续跟踪跨批次资源范围配置。
- Comment: 当前原型已为 Batch 5 补齐“从模板创建课程”的最小后端闭环：`create_class_draft` 仅允许使用存在且启用中的模板，且会将模板默认值自动回填到 `className`、`classType`、价格、人数、课程说明/规则/FAQ 等字段；显式 payload 优先于模板默认值，`None`/空字符串会触发回填。下一最小缺口切换为复制建课与模板管理写路径。
