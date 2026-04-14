# 拼课课程系统 Batch 0 测试与验收文档

Date: 2026-04-11  
Status: Draft for Design Review  
Role: QA / Test  
Owner: Hermes  
Depends on:
- `docs/plans/2026-04-11-group-class-kanban-prd.md`
- `docs/plans/2026-04-11-group-class-kanban-delivery-governance.md`
- `docs/plans/2026-04-11-group-class-kanban-ui-design.md`
- `docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
- `docs/plans/2026-04-11-group-class-kanban-acpx-implementation-plan.md`

---

## 1. 文档目的

本文档用于从 QA / Test 视角定义拼课课程系统在 Batch 0 阶段的测试与验收基线，作为后续 Batch 1 至 Batch 4 开发、联调、验收、审批的统一依据。

本文档目标：
1. 明确各 Batch 的测试范围与验收边界
2. 冻结关键测试策略、环境、数据准备要求
3. 提前定义角色权限、状态流转、接口契约、非功能基线的验收口径
4. 为每个小功能点提供可复用的自测记录与验收记录模板
5. 满足研发治理文档对“先设计、后开发、每步可验证、每步有记录”的要求

说明：
1. Batch 0 不直接验收业务功能上线结果
2. Batch 0 的核心任务是完成测试设计冻结、验收口径冻结、模板初始化
3. 后续各 Batch 必须在本文件基础上补充执行结果，不得脱离本文档另起口径

---

## 2. 测试范围

## 2.1 Batch 0 范围
Batch 0 聚焦“设计与治理初始化”，测试与验收范围包括：
1. PRD、UI、架构、治理、实施计划之间的一致性检查
2. 批次范围、角色权限、状态流转、接口契约是否冻结
3. 测试策略、测试环境、测试数据、记录模板是否完备
4. issue log / progress 文档是否已初始化
5. 是否满足进入 Batch 1 的前置条件

Batch 0 不包括：
1. 真实业务功能代码验证
2. 前后端联调结果验证
3. 性能压测与生产级安全压测
4. 支付、通知、CRM、BI 等后续能力验证

## 2.2 按批次范围说明

| Batch | 批次目标 | QA 关注重点 | 结果类型 |
|---|---|---|---|
| Batch 0 | 设计与治理初始化 | 文档一致性、契约冻结、模板完备、门禁清晰 | 设计验收 |
| Batch 1 | 数据模型与后台课程管理骨架 | 数据结构、后台列表、建课表单、草稿保存 | 功能验收 |
| Batch 2 | 角色权限与审核发布流 | 角色权限、提交审核、审核通过/驳回、前台可见性 | 功能验收 |
| Batch 3 | 前台课程看板与详情页 | 前台列表、详情、状态标签、人数文案、移动端基本可用性 | 功能验收 |
| Batch 4 | 报名、候补、报名管理 | 报名提交、候补提交、后台报名管理、字段校验、关联关系 | 功能验收 |
| Batch 5 | 模板能力与运营效率增强 | 模板回填、复制创建、筛选增强 | 增强验收 |
| Batch 6 | 增强项（可选） | 自动化状态、通知、候补转正、支付锁位 | 后续规划 |

---

## 3. 测试策略

## 3.1 总体策略
采用“文档冻结先行、功能点闭环验收、按批次逐层推进”的测试策略。

执行原则：
1. 先验证设计正确，再验证实现正确
2. 关键路径优先于边缘路径
3. 权限路径、状态路径、接口契约路径必须重点覆盖
4. 每个小功能点必须具备最小可验证方式
5. 发现问题先记录 issue，再推动修复与回归

## 3.2 测试层次

| 层次 | 目标 | Batch 0 要求 |
|---|---|---|
| 文档级测试 | 验证需求、设计、架构、治理是否一致 | 必须完成 |
| 契约级测试 | 验证字段、状态、权限、接口口径是否冻结 | 必须完成 |
| 功能级测试 | 验证页面、接口、交互、校验是否符合设计 | 作为后续 Batch 基线提前定义 |
| 流程级测试 | 验证端到端业务链路 | 先定义关键路径，后续批次执行 |
| 非功能测试 | 验证可用性、日志、审计、错误处理等 | 定义基线，后续按批次执行 |

## 3.3 覆盖重点
1. 角色权限边界
2. 课程状态机
3. 前后台课程可见性
4. 课程字段与表单字段契约
5. 报名与候补数据结构
6. 审计、日志、错误返回规范
7. 文档更新和审批门禁

---

## 4. 测试环境

## 4.1 文档评审环境
1. 文档仓库主分支或评审分支
2. Markdown 可查看环境
3. issue log 与 progress 文档可写环境
4. 统一评审版本号或提交记录

## 4.2 后续开发测试环境基线
为后续 Batch 预定义如下环境：
1. 本地开发环境
2. 联调测试环境
3. 预发布验收环境

建议约束：
1. 各环境使用同一状态枚举与字段命名
2. 测试环境应保留审计日志与错误日志
3. 前后端联调环境必须基于冻结 API 契约

## 4.3 环境配置基线
1. 关系型数据库：MySQL 或 PostgreSQL
2. 对象存储：课程封面上传可选接入
3. 认证源：后台账号体系或现有平台用户体系
4. 日志能力：应用日志、审计日志、错误日志可分离
5. 可选缓存：Redis 非强依赖

---

## 5. 数据准备

## 5.1 Batch 0 数据准备目标
Batch 0 以“样例数据与验收样本”准备为主，不要求真实落库业务数据，但必须准备以下测试样本：

1. 角色样本
   - 超级管理员
   - 课程管理员
   - 指定发起人
   - 普通用户

2. 课程状态样本
   - `DRAFT`
   - `PENDING_REVIEW`
   - `OPEN_FOR_ENROLLMENT`
   - `ALMOST_CONFIRMED`
   - `CONFIRMED`
   - `FULL`
   - `WAITLIST_OPEN`
   - `IN_PROGRESS`
   - `ENDED`
   - `CANCELLED`
   - `REJECTED`

3. 报名类型样本
   - `ENROLLMENT`
   - `WAITLIST`
   - `TRIAL`

4. 报名状态样本
   - `SUBMITTED`
   - `VALID`
   - `INVALID`
   - `WAITLISTED`
   - `TRANSFERRED`
   - `CANCELLED`

## 5.2 课程样例数据建议

| 样例 ID | 用途 | 关键状态 |
|---|---|---|
| CLASS-001 | 草稿编辑 | `DRAFT` |
| CLASS-002 | 提交审核 | `PENDING_REVIEW` |
| CLASS-003 | 前台报名展示 | `OPEN_FOR_ENROLLMENT` |
| CLASS-004 | 即将成班文案校验 | `ALMOST_CONFIRMED` |
| CLASS-005 | 已成班展示 | `CONFIRMED` |
| CLASS-006 | 满员切换候补 | `FULL` |
| CLASS-007 | 候补登记 | `WAITLIST_OPEN` |
| CLASS-008 | 进行中展示限制 | `IN_PROGRESS` |
| CLASS-009 | 已结束/不可编辑 | `ENDED` |
| CLASS-010 | 已取消/不可恢复 | `CANCELLED` |
| CLASS-011 | 驳回后回草稿 | `REJECTED` |

## 5.3 报名样例数据建议

| 样例 ID | 类型 | 用途 |
|---|---|---|
| REG-001 | `ENROLLMENT` | 正常报名流程 |
| REG-002 | `WAITLIST` | 候补登记流程 |
| REG-003 | `TRIAL` | 试听申请流程 |
| REG-004 | `ENROLLMENT` + `INVALID` | 无效报名处理 |
| REG-005 | `WAITLIST` + `WAITLISTED` | 候补状态查看 |

## 5.4 数据校验基线
1. `max_students >= min_students`
2. `signup_deadline <= start_date`
3. `end_date >= start_date`
4. `deposit_amount <= price_amount`
5. 发布前必填字段齐全
6. 报名类型与字段要求一致
7. 驳回必须包含理由

---

## 6. Batch 0 功能级测试用例

说明：Batch 0 的“功能级测试”指设计交付物与治理交付物的可用性测试，不是业务代码测试。

## 6.1 用例清单

| 用例 ID | 功能点 | 验证目标 | 预期结果 |
|---|---|---|---|
| B0-TC-001 | PRD 与 ACPX 计划对齐 | 批次目标、范围、交付边界一致 | 无冲突项 |
| B0-TC-002 | UI 与 PRD 对齐 | 页面清单、字段、状态展示符合 PRD | 无缺页、无缺字段、无冲突状态 |
| B0-TC-003 | 架构与 PRD 对齐 | 数据模型、权限、状态机覆盖 PRD 关键需求 | 关键需求均有落点 |
| B0-TC-004 | UI 与架构字段对齐 | 创建页/详情页/列表页字段可映射到数据模型 | 字段命名与含义一致 |
| B0-TC-005 | 权限矩阵冻结 | 4 类角色职责与限制清晰 | 无模糊权限点 |
| B0-TC-006 | 状态机冻结 | 课程状态、报名类型、报名状态定义完整 | 状态可追踪、无隐式状态 |
| B0-TC-007 | API 契约冻结 | 关键接口输入输出、动作字段、错误口径明确 | 前后端可并行 |
| B0-TC-008 | 测试文档完整性 | 含策略、环境、数据、模板、门禁、风险 | 满足治理规范 |
| B0-TC-009 | issue/progress 初始化 | 文档已建立且字段可用于追踪 | 满足治理规范 |
| B0-TC-010 | Batch 1 进入条件检查 | 设计、契约、测试、治理四类前置齐备 | 可进入 Batch 1 或明确阻塞 |

## 6.2 执行步骤示例
1. 逐份阅读 PRD、UI、架构、治理、实施计划文档
2. 建立字段映射、状态映射、角色映射清单
3. 对照检查冲突、缺失、未冻结项
4. 记录 issue 并分级
5. 输出评审结论与是否允许进入 Batch 1

---

## 7. 后续批次功能级测试基线

本节在 Batch 0 即冻结，后续 Batch 执行时逐项补充结果。

## 7.1 Batch 1 功能用例基线

| 用例 ID | 功能点 | 验证目标 |
|---|---|---|
| B1-TC-001 | 课程数据模型 | `classes` 字段、约束、索引落地正确 |
| B1-TC-002 | 报名数据模型 | `registrations` 基础结构落地正确 |
| B1-TC-003 | 模板数据模型 | `class_templates` 基础结构可用 |
| B1-TC-004 | 后台课程列表页 | 列表字段与 UI 设计一致 |
| B1-TC-005 | 新建课程页字段展示 | 表单模块与必填标识正确 |
| B1-TC-006 | 保存草稿 | 草稿可创建、可回填、可编辑 |
| B1-TC-007 | 草稿列表展示 | 草稿在后台可见，前台不可见 |

## 7.2 Batch 2 功能用例基线

| 用例 ID | 功能点 | 验证目标 |
|---|---|---|
| B2-TC-001 | 角色模型接入 | 角色集返回正确 |
| B2-TC-002 | 资源级权限校验 | 接口侧限制有效，不仅前端隐藏 |
| B2-TC-003 | 提交审核 | `DRAFT -> PENDING_REVIEW` 正确 |
| B2-TC-004 | 审核通过 | `PENDING_REVIEW -> OPEN_FOR_ENROLLMENT` 正确 |
| B2-TC-005 | 审核驳回 | `PENDING_REVIEW -> REJECTED -> DRAFT` 可追踪 |
| B2-TC-006 | 前台可见性过滤 | 草稿/待审核/驳回课程前台不可见 |

## 7.3 Batch 3 功能用例基线

| 用例 ID | 功能点 | 验证目标 |
|---|---|---|
| B3-TC-001 | 前台课程列表接口 | 仅返回前台可见课程 |
| B3-TC-002 | 课程卡片展示 | 名称、时间、价格、人数、状态、CTA 正确 |
| B3-TC-003 | 状态标签展示 | UI 文案符合状态规范 |
| B3-TC-004 | 差额人数文案 | “还差 X 人成班 / 已成班 / 已满员”逻辑正确 |
| B3-TC-005 | 课程详情页 | 决策信息、规则、FAQ、CTA 完整；后端最小契约应覆盖 `courseSubtitle`、适合/不适合人群、课程目标、排课摘要、课时数、成班/请假/候补/不成班规则与 FAQ 摘要字段，并具备最小数据有效性校验 |
| B3-TC-006 | 移动端基本可用性 | 首屏、CTA、表单入口可正常操作 |

## 7.4 Batch 4 功能用例基线

> Execution Update (2026-04-12): 当前原型已完成 B4-TC-001（报名表单基础提交）、B4-TC-003（候补表单提交）与 B4-TC-007（报名/候补数据与课程关联正确）的最小后端契约验证；后续 Batch 4 测试优先聚焦后台报名管理列表、报名详情/备注、资源归属过滤与更细粒度状态管理回归。

| 用例 ID | 功能点 | 验证目标 |
|---|---|---|
| B4-TC-001 | 报名表单提交 | 必填校验、成功反馈、数据落库正确 |
| B4-TC-002 | 报名重复提交防护 | 提交中按钮禁用，避免重复提交 |
| B4-TC-003 | 候补表单提交 | 满员/候补中状态下可正常提交 |
| B4-TC-004 | CTA 切换 | 满员课程前台显示“加入候补” |
| B4-TC-005 | 报名管理列表 | 后台可查看报名/候补/试听记录 |
| B4-TC-006 | 报名详情与备注 | 跟进备注可保存并回显 |
| B4-TC-007 | 课程与报名关联 | 课程人数、报名列表、状态一致 |
| B4-TC-008 | 报名状态管理 | 后台可标记有效/无效/取消并回显最新状态 |

## 7.5 Batch 5 功能用例基线

> Execution Update (2026-04-12): 当前原型已完成 B5-TC-003（从模板创建课程）的最小后端保护：`create_class_draft` 仅允许使用存在且启用中的模板，模板不存在返回 `CLASS_NOT_FOUND`，模板停用返回 `VALIDATION_INVALID_ARGUMENT`；最新验证结果为 `tests/group_class_backend/classes/test_create_class_draft.py tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `45 passed in 0.51s`，`tests/group_class_backend -q` → `84 passed in 0.59s`。后续 Batch 5 测试优先聚焦模板字段自动回填、复制建课与模板管理写路径。

| 用例 ID | 功能点 | 验证目标 |
|---|---|---|
| B5-TC-001 | 模板模型与接口 | `class_templates` 结构、启用态与基础读写契约可用 |
| B5-TC-002 | 模板管理基础能力 | 后台可新增/查看/停用模板 |
| B5-TC-003 | 从模板创建课程 | 仅可使用存在且启用中的模板建课，并正确记录模板来源 |
| B5-TC-004 | 模板字段自动回填 | 模板默认字段可回填到课程草稿，且允许按规则覆盖 |
| B5-TC-005 | 复制创建课程 | 可基于既有课程快速生成新草稿，避免复制不可复用状态字段 |
| B5-TC-006 | FAQ/说明复用 | FAQ 与说明文案可从模板/既有课程复用 |
| B5-TC-007 | 后台筛选增强 | 支持模板来源、状态、负责人等基础筛选 |

---

## 8. 角色与权限验收

## 8.1 角色验收矩阵

| 验收项 | 超级管理员 | 课程管理员 | 指定发起人 | 普通用户 |
|---|---|---|---|---|
| 查看前台课程 | 通过 | 通过 | 通过 | 通过 |
| 查看后台课程列表 | 全部课程 | 权限范围课程 | 仅自己课程 | 不通过 |
| 创建课程草稿 | 通过 | 通过 | 通过 | 不通过 |
| 编辑课程草稿 | 任意 | 权限范围 | 自己创建 | 不通过 |
| 提交审核 | 通过 | 通过 | 通过 | 不通过 |
| 审核通过/驳回 | 通过 | 配置范围内通过 | 不通过 | 不通过 |
| 直接发布 | 通过 | 配置范围内通过 | 不通过 | 不通过 |
| 下架/取消课程 | 通过 | 权限范围 | 不通过 | 不通过 |
| 查看报名数据 | 全量 | 权限范围 | 自己课程 | 不通过 |
| 导出报名名单 | 通过 | 通过 | 不通过 | 不通过 |
| 配置角色权限 | 通过 | 不通过 | 不通过 | 不通过 |

## 8.2 权限验收重点
1. 后端接口必须强校验，不能仅依赖前端按钮显隐
2. `INITIATOR` 默认不可直接发布
3. `CLASS_ADMIN` 是否可审核全部课程必须有明确配置口径
4. 报名数据查询必须按资源归属过滤
5. 课程接口应返回 `actions` 字段供前端展示控制

---

## 9. 状态流转验收

## 9.1 课程状态验收

| 验收项 | 期望 |
|---|---|
| 草稿提交审核 | `DRAFT -> PENDING_REVIEW` |
| 审核通过 | `PENDING_REVIEW -> OPEN_FOR_ENROLLMENT` |
| 审核驳回 | `PENDING_REVIEW -> REJECTED` |
| 驳回退回编辑 | `REJECTED -> DRAFT` |
| 报名中取消 | `OPEN_FOR_ENROLLMENT -> CANCELLED` |
| 报名中满员 | `OPEN_FOR_ENROLLMENT -> FULL` |
| 报名中开放候补 | `OPEN_FOR_ENROLLMENT -> WAITLIST_OPEN` |
| 报名中进入开课 | `OPEN_FOR_ENROLLMENT -> IN_PROGRESS` |
| 已成班进入开课 | `CONFIRMED -> IN_PROGRESS` |
| 开课结束 | `IN_PROGRESS -> ENDED` |

## 9.2 状态验收规则
1. 前台不展示 `DRAFT`、`PENDING_REVIEW`、`REJECTED`
2. 驳回必须填写理由并留痕
3. 已取消课程不可恢复为报名中
4. 已结束课程不可编辑核心字段
5. `FULL` 状态前台主 CTA 必须切换为候补
6. `ALMOST_CONFIRMED` 可作为展示派生，但不能替代主状态落库

## 9.3 报名状态验收
1. 正式报名类型为 `ENROLLMENT`
2. 候补登记类型为 `WAITLIST`
3. 试听申请类型为 `TRIAL`
4. 报名记录状态需支持 `SUBMITTED`、`VALID`、`INVALID`、`WAITLISTED`、`TRANSFERRED`、`CANCELLED`
5. 报名类型与字段要求必须匹配

---

## 10. API / 契约检查

## 10.1 Batch 0 契约检查目标
Batch 0 必须冻结以下契约，以支持前后端并行开发：
1. 状态枚举
2. 角色枚举
3. 数据模型关键字段
4. 页面字段映射
5. 接口输入输出结构
6. 错误返回规范
7. 前端动作控制字段

## 10.2 关键接口清单

| 接口域 | 关键接口 | 核验重点 |
|---|---|---|
| 课程管理 | 创建课程、保存草稿、编辑课程、课程列表、课程详情 | 字段完整、状态正确、权限正确 |
| 审核发布 | 提交审核、审核通过、审核驳回、发布、取消/下架 | 状态流转、审计记录、权限校验 |
| 前台查询 | 课程看板列表、课程详情 | 可见性过滤、状态文案映射 |
| 报名管理 | 报名提交、候补提交、试听提交、报名列表、报名详情 | 字段校验、数据关联、权限过滤 |
| 公共能力 | 当前用户角色与 actions 返回 | 角色并集、动作显式 |

## 10.3 契约检查项
1. 字段命名在 PRD、UI、架构之间一致
2. 必填字段与页面校验规则一致
3. 枚举值必须集中定义，不允许多套文案并存
4. 发布前完整校验规则必须明确
5. 错误返回需可定位问题，不允许模糊失败
6. 审计字段应覆盖创建人、负责人、审核人、发布时间、取消时间
7. 前台接口不得泄露后台内部状态

---

## 11. 非功能检查

## 11.1 Batch 0 非功能基线
Batch 0 先冻结基线，后续各 Batch 执行验证。

## 11.2 检查项

| 类别 | 检查项 | Batch 0 要求 |
|---|---|---|
| 可用性 | 用户端信息层级清晰、CTA 明确、移动端优先 | 设计中已定义 |
| 可维护性 | 模块边界清晰，不平行造轮子 | 架构中已定义 |
| 可测试性 | 关键状态、角色、字段可显式验证 | 契约中已定义 |
| 可审计性 | 关键操作有审计记录与状态历史 | 架构中已定义 |
| 可追踪性 | issue / progress / 自测 / 验收模板完备 | 本文档中已定义 |
| 错误处理 | 错误返回明确、驳回理由必填 | 架构中已定义 |
| 安全性 | 后台写接口鉴权、资源级权限校验 | 架构中已定义 |
| 性能基线 | 前台查询与后台列表支持常规分页和索引 | 架构中已提出 |
| 数据一致性 | 状态、人数、报名关系显式落库 | 架构中已定义 |

## 11.3 后续 Batch 非功能回归重点
1. 前台页面移动端可读性
2. 提交类接口幂等性与重复提交控制
3. 列表分页和筛选性能
4. 审计日志完整性
5. 异常场景提示清晰度

---

## 12. 自测记录模板

```md
# 自测记录

- 功能点名称：
- 所属 Batch：
- 开发负责人：
- 自测日期：
- 自测环境：
- 关联需求/设计：
- 涉及文件：

## 自测前提
- 数据准备：
- 账号角色：
- 依赖条件：

## 自测步骤
1.
2.
3.

## 实际结果
- 

## 预期结果
- 

## 自测结论
- 通过 / 不通过

## 已知限制
- 

## issue 记录
- Issue ID：
```

---

## 13. 验收记录模板

```md
# 验收记录

- 功能点名称：
- 所属 Batch：
- 验收角色：QA / Hermes
- 验收日期：
- 验收环境：
- 验收依据：
  - PRD：
  - UI 设计：
  - 架构设计：
  - 测试文档：
- 关联 issue：

## 验收前提
- 
- 

## 验收步骤
1.
2.
3.

## 验收结果
- 结果：
- 证据：
- 是否符合设计：

## 缺陷与偏差
- 

## 回归要求
- 

## 验收结论
- 通过 / 不通过 / 有条件通过

## 后续处理建议
- 
```

---

## 14. 进入标准与退出标准

## 14.1 Batch 0 进入标准
1. PRD 已完成并明确批次划分
2. 已建立研发治理与交付规范
3. 已形成 ACPX 分批执行计划
4. 已启动 UI 设计与架构设计
5. 已指定 QA / Test 输出测试与验收文档

## 14.2 Batch 0 退出标准
以下条件全部满足，Batch 0 才可申请完成：
1. UI 设计文档完成
2. 架构设计文档完成
3. 测试与验收文档完成
4. issue log 已初始化
5. progress 文档已初始化
6. 角色权限边界已冻结
7. 状态机已冻结
8. API / 数据契约关键项已冻结
9. Batch 1 的测试基线已明确
10. Hermes 完成设计评审并给出结论

## 14.3 后续小功能点通用进入标准
1. 上一依赖功能点已通过审批
2. 相关设计和契约已冻结
3. 测试用例与数据已准备
4. issue / progress 已同步初始化

## 14.4 后续小功能点通用退出标准
1. 开发完成
2. 开发者自测完成并留档
3. QA 验收完成并留档
4. issue 已更新
5. progress 已更新
6. Hermes 审批通过

---

## 15. 阻塞项与风险

## 15.1 当前阻塞项
1. Batch 0 需补齐 `issue log` 文档
2. Batch 0 需补齐 `progress` 文档
3. 若接口契约未进一步落到接口清单级别，Batch 1 前后端并行存在沟通风险

## 15.2 当前风险清单

| 风险 ID | 风险描述 | 影响 | 建议措施 |
|---|---|---|---|
| R-001 | UI 字段与数据模型字段未形成一一映射清单 | 前后端联调返工 | 在 Batch 1 前补字段映射表 |
| R-002 | `ALMOST_CONFIRMED` 为展示态还是主状态理解不一致 | 状态实现混乱 | 统一口径：展示可派生，主状态显式存储优先 |
| R-003 | `CLASS_ADMIN` 审核范围为“全部”还是“权限范围”未完全产品化 | 权限边界争议 | 在 Batch 2 前冻结配置策略 |
| R-004 | 发布、下架、取消的操作口径与按钮文案可能不一致 | 前后台行为偏差 | 在接口契约中补动作定义 |
| R-005 | 报名成功后人数更新、状态更新策略未明确到实现细节 | Batch 4 数据一致性风险 | 在 Batch 4 前补充规则说明 |
| R-006 | issue/progress 若未持续维护，会破坏治理门禁 | 审批无法追踪 | 强制作为退出标准检查 |
| R-007 | 非功能项仅有基线，缺少量化指标 | 后续验收主观化 | 在进入预发布前补充量化指标 |

---

## 16. Review 结论

## 16.1 QA 评审结论
基于当前已阅读文档，Batch 0 的测试与验收设计已具备可执行基础，能够支撑后续 Batch 1 至 Batch 4 的分批开发与验收。

当前结论：
1. PRD、UI、架构、治理、实施计划总体方向一致
2. 角色模型、状态机、数据模型、批次边界已基本冻结
3. Batch 0 测试文档已覆盖策略、环境、数据、模板、门禁、风险
4. 进入 Batch 1 前仍需补齐 issue log 与 progress 文档，并建议补一份字段映射/接口清单

## 16.2 审批建议
建议结论：`有条件通过`

通过条件：
1. 初始化 `docs/plans/2026-04-11-group-class-kanban-issue-log.md`
2. 初始化 `docs/plans/2026-04-11-group-class-kanban-progress.md`
3. 在 Batch 1 开始前补充关键页面字段与数据模型字段映射清单
4. 在 Batch 2 开始前补充审核范围配置口径说明

## 16.3 进入下一阶段建议
满足上述条件后，可进入 Batch 1：数据模型与后台课程管理骨架。

---

## 17. Batch 1 执行记录补充

### 17.1 自测记录

# 自测记录

- 功能点名称：Batch 1 Python 后端原型（课程草稿创建/更新/详情/列表 + SQLite 最小持久化闭环）
- 所属 Batch：Batch 1
- 开发负责人：Hermes
- 自测日期：2026-04-12
- 自测环境：本地 Python 3.11 + SQLite in-memory
- 关联需求/设计：
  - `docs/plans/2026-04-12-group-class-kanban-batch1-python-backend-parallel-plan.md`
  - `docs/plans/2026-04-11-group-class-kanban-batch1-field-mapping-and-contract-freeze.md`
  - `docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
- 涉及文件：
  - `apps/group_class_backend/common/*`
  - `apps/group_class_backend/classes/*`
  - `apps/group_class_backend/persistence/schema.py`
  - `tests/group_class_backend/classes/test_create_class_draft.py`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py`
  - `tests/group_class_backend/persistence/test_schema_definition.py`

## 自测前提
- 数据准备：使用测试内构造的课程草稿样本与 SQLite `:memory:` 数据库。
- 账号角色：后台管理员（通过 `actor_id=admin-001` 模拟）。
- 依赖条件：已先执行 `apply_schema()` 初始化 schema，并确保冻结契约文档已可引用。

## 自测步骤
1. 运行 `tests/group_class_backend/classes/test_create_class_draft.py` 与 `tests/group_class_backend/classes/test_class_queries_and_update.py`，验证课程草稿创建、更新、详情、列表与版本冲突逻辑。
2. 运行 `tests/group_class_backend/persistence/test_schema_definition.py`，验证 `classes` / `registrations` / `class_templates` 的表、索引与关键约束。
3. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q`，验证 Batch 1 当前测试全集。

## 实际结果
- 课程草稿创建、更新、详情、分页列表全部通过测试。
- SQLite repository 闭环测试通过，覆盖 create/update/detail/list 全链路。
- schema 定义测试通过，确认核心索引与约束存在。
- 全量结果：`25 passed in 0.50s`。

## 预期结果
- Batch 1 最小后端骨架具备稳定契约输出。
- `classes`、`registrations`、`class_templates` 三类核心结构具备关系型 schema 表达。
- 后台课程管理相关最小接口可由测试稳定验证。

## 自测结论
- 通过

## 已知限制
- 当前 migration 仍采用原型级 `apply_schema()`，未引入 Alembic / Django migrations。
- 审核发布、权限、前台展示、报名流转仍属于后续 Batch 范围。

## issue 记录
- Issue ID：`B1-ISS-001`（已关闭）

### 17.2 验收记录

# 验收记录

- 功能点名称：Batch 1 Python 后端原型完成验收
- 所属 Batch：Batch 1
- 验收角色：QA / Hermes
- 验收日期：2026-04-12
- 验收环境：本地 Python 3.11 + SQLite in-memory
- 验收依据：
  - PRD：`docs/plans/2026-04-11-group-class-kanban-prd.md`
  - UI 设计：`docs/plans/2026-04-11-group-class-kanban-ui-design.md`
  - 架构设计：`docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - 测试文档：`docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
- 关联 issue：`B1-ISS-001`

## 验收前提
- Batch 1 字段映射与 contract freeze 文档已存在。
- Batch 1 代码、测试、issue、progress 已完成同步。

## 验收步骤
1. 复核 Batch 1 并行开发计划、contract freeze、progress、issue log 是否一致。
2. 复核 `SQLiteClassRepository` 与 schema 定义，确认已满足 Batch 1 对关系型数据结构的最小要求。
3. 执行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 作为最终验收回归。

## 验收结果
- 结果：通过
- 证据：
  - `apps/group_class_backend/persistence/schema.py:1`
  - `tests/group_class_backend/persistence/test_schema_definition.py:15`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py:137`
  - `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `25 passed in 0.50s`
- 是否符合设计：是，已满足 Batch 1 对课程草稿创建/更新/详情/列表、统一契约、核心 schema/索引/约束表达的最小目标。

## 缺陷与偏差
- 无阻断性缺陷。
- 工程化 migration framework 未纳入当前批次交付，按增强项后续跟踪。

## 回归要求
- 后续进入 Batch 2+ 前，任何对 `common` 契约、`classes` 仓储或 schema 的改动，均需回归 `tests/group_class_backend` 全量测试。

## 验收结论
- 通过

## 后续处理建议
- 可宣布当前仓库内 Batch 1 Python 后端原型完成。
- 后续按计划转入 Batch 2 前，先处理尚未关闭的跨批次设计/权限类 issue。

## 18. Batch 2 执行记录补充

### 18.1 自测记录

# 自测记录

- 功能点名称：Batch 2 审核通过最小闭环（B2-TC-004）
- 所属 Batch：Batch 2
- 开发负责人：Hermes
- 自测日期：2026-04-12
- 自测环境：本地 Python 3.11 + SQLite in-memory
- 关联需求/设计：
  - `docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - `docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
  - `docs/plans/2026-04-12-group-class-kanban-batch1-python-backend-parallel-plan.md`
- 涉及文件：
  - `apps/group_class_backend/classes/controller.py`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py`

## 自测前提
- 数据准备：先通过 `create_class_draft()` 创建草稿课程，再执行 `submit_class_review()` 将课程推进到 `PENDING_REVIEW`。
- 账号角色：后台审核人（通过 `actor_id=reviewer-001` 模拟）。
- 依赖条件：课程必须处于 `PENDING_REVIEW` 且携带正确 `version`；SQLite 场景需先执行 `apply_schema()`。

## 自测步骤
1. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q`。
2. 重点复核 `test_approve_class_review_transitions_pending_review_to_open_for_enrollment`、`test_approve_class_review_rejects_non_pending_review_status`、`test_approve_class_review_returns_version_conflict`、`test_sqlite_repository_persists_approve_review_flow`。
3. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做全量回归。

## 实际结果
- 审核通过成功时，课程状态从 `PENDING_REVIEW` 迁移到 `OPEN_FOR_ENROLLMENT`，`version` 自增到 3，`actions` 收敛为 `["view"]`。
- 非 `PENDING_REVIEW` 状态调用会返回 `VALIDATION_INVALID_ARGUMENT`，版本不匹配会返回 `CLASS_VERSION_CONFLICT`。
- SQLite repository 与内存仓储场景均通过。
- targeted 结果：`14 passed in 0.46s`。
- 全量结果：`33 passed in 0.63s`。

## 预期结果
- 满足 B2-TC-004：`PENDING_REVIEW -> OPEN_FOR_ENROLLMENT` 正确。
- 维持统一错误码、版本并发保护与动作字段契约。
- 不破坏已有 Batch 1 / Batch 2 提交审核能力。

## 自测结论
- 通过

## 已知限制
- 当前仅实现 Batch 2 的“审核通过”最小闭环，尚未实现角色权限强校验、审核驳回与前台可见性过滤。
- 审核通过后的发布/下架等后续动作仍待 Batch 2 后续最小功能点继续实现。

## issue 记录
- Issue ID：`B2-ISS-001`（已关闭）；跨批次权限口径问题仍受 `B0-ISS-004` 约束。

### 18.2 验收记录

# 验收记录

- 功能点名称：Batch 2 审核通过最小闭环（B2-TC-004）
- 所属 Batch：Batch 2
- 验收角色：QA / Hermes
- 验收日期：2026-04-12
- 验收环境：本地 Python 3.11 + SQLite in-memory
- 验收依据：
  - PRD：`docs/plans/2026-04-11-group-class-kanban-prd.md`
  - 架构设计：`docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - 测试文档：`docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
- 关联 issue：`B2-ISS-001`, `B0-ISS-004`

## 验收前提
- Batch 1 原型已完成，且 Batch 2 提交审核最小闭环已稳定通过。
- 当前验收仅覆盖“审核通过”最小状态流转，不扩大到权限模型、驳回流转与前台可见性过滤。

## 验收步骤
1. 复核 `approve_class_review` 的状态流转、错误码与动作字段是否对齐 B2-TC-004。
2. 复核内存仓储与 SQLite repository 两条路径是否都具备相同行为。
3. 执行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做回归验收。

## 验收结果
- 结果：通过
- 证据：
  - `apps/group_class_backend/classes/controller.py:255`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py:110`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py:193`
  - `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `33 passed in 0.63s`
- 是否符合设计：是，已满足测试基线中 B2-TC-004 对 `PENDING_REVIEW -> OPEN_FOR_ENROLLMENT` 的最小要求，并保持版本冲突与非法状态保护。

## 缺陷与偏差
- 未纳入角色/资源级权限校验，当前验收仅覆盖状态流转最小闭环。
- 审核驳回与前台可见性过滤仍待后续 Batch 2 功能点实现。

## 回归要求
- 后续进入 Batch 2 下一功能点前，任何对 `ClassStatus`、`default_actions_for_status()`、`submit_class_review()`、`approve_class_review()` 的改动，均需回归 `tests/group_class_backend` 全量测试。

## 验收结论
- 通过

## 后续处理建议
- 下一步应按最小粒度继续实现 Batch 2 的审核驳回闭环，或在此之前补齐角色/资源级权限强校验。

---

## 19. Batch 2 审核驳回执行记录补充

### 19.1 自测记录

# 自测记录

- 功能点名称：Batch 2 审核驳回最小闭环（B2-TC-005）
- 所属 Batch：Batch 2
- 开发负责人：Hermes
- 自测日期：2026-04-12
- 自测环境：本地 Python 3.11 + SQLite in-memory
- 关联需求/设计：
  - `docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - `docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
  - `docs/plans/2026-04-12-group-class-kanban-batch1-python-backend-parallel-plan.md`
- 涉及文件：
  - `apps/group_class_backend/classes/controller.py`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py`

## 自测前提
- 数据准备：先通过 `create_class_draft()` 创建草稿课程，再执行 `submit_class_review()` 将课程推进到 `PENDING_REVIEW`。
- 账号角色：后台审核人（通过 `actor_id=reviewer-001` 模拟）。
- 依赖条件：课程必须处于 `PENDING_REVIEW` 且携带正确 `version`；SQLite 场景需先执行 `apply_schema()`。

## 自测步骤
1. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_class_queries_and_update.py -q`。
2. 重点复核 `test_reject_class_review_transitions_pending_review_to_rejected`、`test_reject_class_review_rejects_non_pending_review_status`、`test_reject_class_review_returns_version_conflict`、`test_sqlite_repository_persists_reject_review_flow`。
3. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做全量回归。

## 实际结果
- 审核驳回成功时，课程状态从 `PENDING_REVIEW` 迁移到 `REJECTED`，`version` 自增到 3，`actions` 收敛为 `["view", "edit", "submit_review"]`。
- 非 `PENDING_REVIEW` 状态调用会返回 `VALIDATION_INVALID_ARGUMENT`，版本不匹配会返回 `CLASS_VERSION_CONFLICT`。
- SQLite repository 与内存仓储场景均通过。
- targeted 结果：`18 passed in 0.46s`。
- 全量结果：`37 passed in 0.51s`。

## 预期结果
- 满足 B2-TC-005：`PENDING_REVIEW -> REJECTED` 正确。
- 维持统一错误码、版本并发保护与动作字段契约。
- 驳回后允许返修并重新提交审核，不破坏已有 Batch 1 / Batch 2 能力。

## 自测结论
- 通过

## 已知限制
- 当前仅实现 Batch 2 的“审核驳回”最小闭环，尚未实现角色/资源级权限强校验与驳回原因结构化落库。
- 驳回后的状态历史查询、审核意见详情与前台可见性过滤仍待 Batch 2 后续最小功能点继续实现。

## issue 记录
- Issue ID：`B2-ISS-002`（已关闭）；跨批次权限口径问题仍受 `B0-ISS-004` 约束。

### 19.2 验收记录

# 验收记录

- 功能点名称：Batch 2 审核驳回最小闭环（B2-TC-005）
- 所属 Batch：Batch 2
- 验收角色：QA / Hermes
- 验收日期：2026-04-12
- 验收环境：本地 Python 3.11 + SQLite in-memory
- 验收依据：
  - PRD：`docs/plans/2026-04-11-group-class-kanban-prd.md`
  - 架构设计：`docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - 测试文档：`docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
- 关联 issue：`B2-ISS-002`, `B0-ISS-004`

## 验收前提
- Batch 1 原型已完成，且 Batch 2 提交审核、审核通过最小闭环已稳定通过。
- 当前验收仅覆盖“审核驳回”最小状态流转，不扩大到权限模型、审核意见结构化落库与状态历史查询。

## 验收步骤
1. 复核 `reject_class_review` 的状态流转、错误码与动作字段是否对齐 B2-TC-005。
2. 复核内存仓储与 SQLite repository 两条路径是否都具备相同行为。
3. 执行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做回归验收。

## 验收结果
- 结果：通过
- 证据：
  - `apps/group_class_backend/classes/controller.py:302`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py:227`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py:310`
  - `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `37 passed in 0.51s`
- 是否符合设计：是，已满足最小驳回闭环对 `PENDING_REVIEW -> REJECTED` 的要求，并保持版本冲突与非法状态保护。

## 缺陷与偏差
- 未纳入角色/资源级权限校验，当前验收仅覆盖状态流转最小闭环。
- 驳回原因结构化落库、状态历史查询与前台可见性过滤仍待后续 Batch 2 功能点实现。

## 回归要求
- 后续进入 Batch 2 下一功能点前，任何对 `ClassStatus`、`default_actions_for_status()`、`submit_class_review()`、`approve_class_review()`、`reject_class_review()` 的改动，均需回归 `tests/group_class_backend` 全量测试。

## 验收结论
- 通过

## 后续处理建议
- 下一步应按最小粒度继续实现 Batch 2 的角色/资源级权限强校验，并同步明确 `CLASS_ADMIN` 的默认审核/驳回范围。 

---

## 20. Batch 4 执行记录补充

### 20.1 自测记录

# 自测记录

- 功能点名称：Batch 4 后台报名列表/权限过滤最小闭环（B4-TC-005）
- 所属 Batch：Batch 4
- 开发负责人：Hermes
- 自测日期：2026-04-12
- 自测环境：本地 Python 3.11 + SQLite in-memory
- 关联需求/设计：
  - `docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - `docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
  - `docs/plans/2026-04-11-group-class-kanban-acpx-implementation-plan.md`
- 涉及文件：
  - `apps/group_class_backend/registrations/controller.py`
  - `tests/group_class_backend/registrations/test_registration_commands.py`

## 自测前提
- 数据准备：分别构造一个由 `admin-001` 创建的课程和一个由 `initiator-002` 创建的课程，并为两门课写入报名记录。
- 账号角色：通过 `actor_roles` 显式模拟 `INITIATOR`、`CLASS_ADMIN`、`SUPER_ADMIN` 与普通 `USER`。
- 依赖条件：SQLite 场景需先执行 `apply_schema()`，并保证课程状态允许报名，以便真实写入列表数据。

## 自测步骤
1. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q`。
2. 重点复核 `test_list_registrations_returns_only_owned_class_records_for_initiator`、`test_list_registrations_rejects_user_without_backoffice_roles`、`test_list_registrations_persists_sqlite_filtering_for_initiator`。
3. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做全量回归。

## 实际结果
- `INITIATOR` 仅能看到自己创建课程的报名记录，其他课程报名在后端被过滤。
- 缺少后台角色的用户访问列表会返回 `PERMISSION_DENIED`。
- SQLite repository 与内存仓储场景下的过滤结果保持一致。
- targeted 结果：`9 passed in 0.45s`。
- 全量结果：`69 passed in 0.59s`。

## 预期结果
- 满足 B4-TC-005：后台可查看报名记录列表。
- 报名数据查询遵守设计文档中的角色 + 资源归属联合判断，不仅依赖前端显隐。
- 不破坏既有 Batch 4 报名/候补提交、课程人数联动与 SQLite 持久化能力。

## 自测结论
- 通过

## 已知限制
- 当前仅实现后台报名列表最小只读闭环，尚未提供单条报名详情读取、备注更新、导出能力。
- `CLASS_ADMIN` 的更细粒度课程范围配置仍未产品化，继续由 `B0-ISS-004` 跟踪。

## issue 记录
- Issue ID：`B4-ISS-001`（已关闭）；跨批次资源范围配置问题仍受 `B0-ISS-004` 约束。

### 20.2 验收记录

# 验收记录

- 功能点名称：Batch 4 后台报名列表/权限过滤最小闭环（B4-TC-005）
- 所属 Batch：Batch 4
- 验收角色：QA / Hermes
- 验收日期：2026-04-12
- 验收环境：本地 Python 3.11 + SQLite in-memory
- 验收依据：
  - PRD：`docs/plans/2026-04-11-group-class-kanban-prd.md`
  - 架构设计：`docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - 测试文档：`docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
- 关联 issue：`B4-ISS-001`, `B0-ISS-004`

## 验收前提
- Batch 3 后端能力与 Batch 4 报名/候补提交最小闭环均已稳定通过。
- 当前验收仅覆盖后台报名列表最小读取与资源归属过滤，不扩大到详情页、跟进备注编辑、导出能力。

## 验收步骤
1. 复核 `list_registrations()` 是否仅允许 `CLASS_ADMIN` / `SUPER_ADMIN` / `INITIATOR` 访问，并检查 `INITIATOR` 仅可见自己创建课程的报名记录。
2. 复核后台列表返回字段是否满足当前最小管理口径：课程名、报名类型、状态、联系人、学生信息、提交时间、备注信息。
3. 执行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做回归验收。

## 验收结果
- 结果：通过
- 证据：
  - `apps/group_class_backend/registrations/controller.py:98`
  - `tests/group_class_backend/registrations/test_registration_commands.py:240`
  - `tests/group_class_backend/registrations/test_registration_commands.py:327`
  - `tests/group_class_backend/registrations/test_registration_commands.py:347`
  - `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `69 passed in 0.59s`
- 是否符合设计：是，已满足 Batch 4 对“后台可查看报名记录、报名数据查询按课程权限过滤”的最小验收口径。

## 缺陷与偏差
- 尚未实现报名详情读取、备注更新与导出名单。
- `CLASS_ADMIN` 的课程责任范围仍为最小实现假设，后续若产品冻结更细粒度规则需继续补齐。

## 回归要求
- 后续对 `list_registrations()`、报名权限判断函数或 `registrations` / `classes` 关联字段的任何改动，均需回归 `tests/group_class_backend` 全量测试。

## 验收结论
- 通过

## 后续处理建议
- 下一步可继续按最小粒度推进 Batch 4 的报名详情/备注能力。

---

## 21. Batch 4 报名详情/备注执行记录补充

### 21.1 自测记录

# 自测记录

- 功能点名称：Batch 4 报名详情/备注最小闭环（B4-TC-006）
- 所属 Batch：Batch 4
- 开发负责人：Hermes
- 自测日期：2026-04-12
- 自测环境：本地 Python 3.11 + SQLite in-memory
- 关联需求/设计：
  - `docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - `docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
  - `docs/plans/2026-04-11-group-class-kanban-acpx-implementation-plan.md`
- 涉及文件：
  - `apps/group_class_backend/registrations/controller.py`
  - `apps/group_class_backend/registrations/repository.py`
  - `tests/group_class_backend/registrations/test_registration_commands.py`

## 自测前提
- 数据准备：先创建处于可报名状态的课程并写入至少一条报名记录，再分别在 in-memory 与 SQLite 场景下读取详情、更新备注。
- 账号角色：通过 `actor_roles` 显式模拟 `INITIATOR`、`SUPER_ADMIN` 与非归属发起人访问场景。
- 依赖条件：SQLite 场景需先执行 `apply_schema()`；报名记录需关联到真实存在的课程，便于复用课程创建人资源归属校验。

## 自测步骤
1. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q`。
2. 重点复核 `test_get_registration_detail_and_update_notes_for_owned_class_initiator`、`test_get_registration_detail_rejects_unowned_initiator`、`test_update_registration_notes_persists_in_sqlite`。
3. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做全量回归。

## 实际结果
- 后台可读取单条报名详情，返回课程名、报名类型、状态、联系人、学生信息、用户备注、跟进备注与更新时间。
- `INITIATOR` 仅能访问自己创建课程下的报名详情；非归属发起人访问会返回 `PERMISSION_DENIED`。
- 备注更新后可立即在详情接口回显，且 SQLite repository 与内存仓储场景行为一致。
- targeted 结果：`12 passed in 0.67s`。
- 全量结果：`72 passed in 0.58s`。

## 预期结果
- 满足 B4-TC-006：后台可查看报名详情并保存/回显备注。
- 报名详情与备注写路径继续遵守角色 + 资源归属联合判断，不仅依赖前端显隐。
- 不破坏既有 Batch 4 报名/候补提交、后台报名列表与 SQLite 持久化能力。

## 自测结论
- 通过

## 已知限制
- 当前仅实现报名详情读取与备注更新最小闭环，尚未提供导出名单与更细粒度报名状态流转。
- `CLASS_ADMIN` 的更细粒度课程范围配置仍未产品化，继续由 `B0-ISS-004` 跟踪。

## issue 记录
- Issue ID：`B4-ISS-001`（已关闭）；跨批次资源范围配置问题仍受 `B0-ISS-004` 约束。

### 21.2 验收记录

# 验收记录

- 功能点名称：Batch 4 报名详情/备注最小闭环（B4-TC-006）
- 所属 Batch：Batch 4
- 验收角色：QA / Hermes
- 验收日期：2026-04-12
- 验收环境：本地 Python 3.11 + SQLite in-memory
- 验收依据：
  - PRD：`docs/plans/2026-04-11-group-class-kanban-prd.md`
  - 架构设计：`docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - 测试文档：`docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
- 关联 issue：`B4-ISS-001`, `B0-ISS-004`

## 验收前提
- Batch 3 后端能力、Batch 4 报名/候补提交与后台报名列表最小闭环均已稳定通过。
- 当前验收仅覆盖报名详情读取与备注更新最小闭环，不扩大到导出能力与更细粒度报名状态管理。

## 验收步骤
1. 复核 `get_registration_detail()` 与 `update_registration_notes()` 是否仅允许 `CLASS_ADMIN` / `SUPER_ADMIN` / `INITIATOR` 访问，并检查 `INITIATOR` 仅可操作自己创建课程下的报名记录。
2. 复核详情返回字段是否满足当前最小管理口径：课程名、报名类型、状态、联系人、学生信息、用户备注、跟进备注、更新时间。
3. 执行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做回归验收。

## 验收结果
- 结果：通过
- 证据：
  - `apps/group_class_backend/registrations/controller.py:98`
  - `apps/group_class_backend/registrations/controller.py:190`
  - `apps/group_class_backend/registrations/controller.py:213`
  - `tests/group_class_backend/registrations/test_registration_commands.py:423`
  - `tests/group_class_backend/registrations/test_registration_commands.py:491`
  - `tests/group_class_backend/registrations/test_registration_commands.py:530`
  - `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `72 passed in 0.58s`
- 是否符合设计：是，已满足 Batch 4 对“后台可查看报名详情、可保存并回显跟进备注、报名数据查询按课程权限过滤”的最小验收口径。

## 缺陷与偏差
- 尚未实现导出报名名单。
- `CLASS_ADMIN` 的课程责任范围仍为最小实现假设，后续若产品冻结更细粒度规则需继续补齐。

## 回归要求
- 后续对 `get_registration_detail()`、`update_registration_notes()`、报名权限判断函数或 `registrations` / `classes` 关联字段的任何改动，均需回归 `tests/group_class_backend` 全量测试。

## 验收结论
- 通过

## 后续处理建议
- 下一步可在 Batch 4/5 交界处评估导出名单或更细粒度报名状态管理能力。

---

## 22. Batch 4 报名状态管理执行记录补充

### 22.1 自测记录

# 自测记录

- 功能点名称：Batch 4 报名状态管理最小闭环（B4-TC-008）
- 所属 Batch：Batch 4
- 开发负责人：Hermes
- 自测日期：2026-04-12
- 自测环境：本地 Python 3.11 + SQLite in-memory
- 关联需求/设计：
  - `docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - `docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
  - `docs/plans/2026-04-11-group-class-kanban-acpx-implementation-plan.md`
- 涉及文件：
  - `apps/group_class_backend/registrations/controller.py`
  - `tests/group_class_backend/registrations/test_registration_commands.py`

## 自测前提
- 数据准备：先创建处于可报名或候补开放状态的课程并写入报名记录，再分别在 in-memory 与 SQLite 场景下执行状态更新。
- 账号角色：通过 `actor_roles` 显式模拟 `INITIATOR`、`SUPER_ADMIN` 与非归属发起人访问场景。
- 依赖条件：SQLite 场景需先执行 `apply_schema()`；报名记录需关联到真实存在的课程，便于复用课程创建人资源归属校验与详情回显。

## 自测步骤
1. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend/registrations/test_registration_commands.py -q`。
2. 重点复核 `test_update_registration_status_marks_owned_class_registration_valid_and_preserves_counts`、`test_update_registration_status_rejects_unowned_initiator`、`test_update_registration_status_rejects_unknown_status_value`、`test_update_registration_status_persists_in_sqlite`。
3. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做全量回归。

## 实际结果
- 后台可将报名状态更新为 `VALID` / `INVALID` / `CANCELLED`，并在更新响应与详情接口中回显最新状态。
- `INITIATOR` 仅能操作自己创建课程下的报名记录；非归属发起人访问会返回 `PERMISSION_DENIED`。
- 非法状态值会返回 `VALIDATION_INVALID_ARGUMENT`，SQLite repository 与内存仓储场景行为一致。
- targeted 结果：`15 passed in 0.47s`。
- 全量结果：`79 passed in 0.58s`。

## 预期结果
- 满足 B4-TC-008：后台可标记报名有效/无效/取消并回显最新状态。
- 报名状态写路径继续遵守角色 + 资源归属联合判断，不仅依赖前端显隐。
- 不破坏既有 Batch 4 报名/候补提交、后台报名列表、详情备注与 SQLite 持久化能力。

## 自测结论
- 通过

## 已知限制
- 当前仅实现报名状态最小手动更新闭环，尚未提供导出名单、自动转正或更复杂状态机。
- `CLASS_ADMIN` 的更细粒度课程范围配置仍未产品化，继续由 `B0-ISS-004` 跟踪。

## issue 记录
- Issue ID：`B4-ISS-001`（已关闭）；跨批次资源范围配置问题仍受 `B0-ISS-004` 约束。

### 22.2 验收记录

# 验收记录

- 功能点名称：Batch 4 报名状态管理最小闭环（B4-TC-008）
- 所属 Batch：Batch 4
- 验收角色：QA / Hermes
- 验收日期：2026-04-12
- 验收环境：本地 Python 3.11 + SQLite in-memory
- 验收依据：
  - PRD：`docs/plans/2026-04-11-group-class-kanban-prd.md`
  - 架构设计：`docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - 测试文档：`docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
- 关联 issue：`B4-ISS-001`, `B0-ISS-004`

## 验收前提
- Batch 3 后端能力、Batch 4 报名/候补提交、后台报名列表与报名详情/备注最小闭环均已稳定通过。
- 当前验收仅覆盖报名状态手动更新最小闭环，不扩大到导出能力、自动转正与更复杂状态机。

## 验收步骤
1. 复核 `update_registration_status()` 是否仅允许 `CLASS_ADMIN` / `SUPER_ADMIN` / `INITIATOR` 访问，并检查 `INITIATOR` 仅可操作自己创建课程下的报名记录。
2. 复核状态更新后是否可在更新响应与 `get_registration_detail()` 中回显最新 `registrationStatus`。
3. 执行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做回归验收。

## 验收结果
- 结果：通过
- 证据：
  - `apps/group_class_backend/registrations/controller.py`
  - `tests/group_class_backend/registrations/test_registration_commands.py`
  - `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `79 passed in 0.58s`
- 是否符合设计：是，已满足 Batch 4 对“后台可标记报名状态且遵守角色 + 课程权限过滤”的最小验收口径。

## 缺陷与偏差
- 尚未实现导出报名名单与自动候补转正。
- `CLASS_ADMIN` 的课程责任范围仍为最小实现假设，后续若产品冻结更细粒度规则需继续补齐。

## 回归要求
- 后续对 `update_registration_status()`、报名权限判断函数、状态枚举或 `registrations` / `classes` 关联字段的任何改动，均需回归 `tests/group_class_backend` 全量测试。

## 验收结论
- 通过

## 后续处理建议
- 下一步可优先评估导出报名名单能力，其次再细化 `CLASS_ADMIN` 资源范围配置。

---

## 23. Batch 5 从模板创建课程执行记录补充

### 23.1 自测记录

# 自测记录

- 功能点名称：Batch 5 从模板创建课程 + 模板字段自动回填最小闭环（B5-TC-003 / B5-TC-004）
- 所属 Batch：Batch 5
- 开发负责人：Hermes
- 自测日期：2026-04-12
- 自测环境：本地 Python 3.11 + SQLite in-memory
- 关联需求/设计：
  - `docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - `docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
  - `docs/plans/2026-04-11-group-class-kanban-acpx-implementation-plan.md`
- 涉及文件：
  - `apps/group_class_backend/classes/controller.py`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py`

## 自测前提
- 数据准备：先准备启用中模板、停用模板与不存在模板 ID 三类场景，再分别调用 `create_class_draft()` 验证模板依赖分支；其中启用模板需带有价格、人数、课程说明/规则/FAQ 等默认值，用于验证自动回填。
- 账号角色：通过 `actor_id=initiator-001` 模拟后台建课发起人。
- 依赖条件：模板仓储需显式注入控制器；全量回归前需激活仓库 `venv`。

## 自测步骤
1. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_create_class_draft.py tests/group_class_backend/classes/test_class_queries_and_update.py -q`。
2. 重点复核 `test_create_class_draft_rejects_missing_template_id` 与 `test_create_class_draft_rejects_inactive_template_id`，确认模板缺失与停用场景分别返回 `CLASS_NOT_FOUND` / `VALIDATION_INVALID_ARGUMENT`。
3. 重点复核模板默认值自动回填断言，确认 `className`、`classType`、价格、人数、课程说明/规则/FAQ 等字段会在 payload 缺省或为空字符串时从模板补齐，且显式 payload 保持优先。
4. 运行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做全量回归。

## 实际结果
- `create_class_draft()` 在携带 `templateId` 时会先校验模板是否存在且启用；不存在模板会被拒绝并返回 `CLASS_NOT_FOUND`。
- 停用模板不会被允许继续建课，并返回 `VALIDATION_INVALID_ARGUMENT`。
- 启用模板的默认值会自动回填到 `className`、`classType`、价格、人数、课程说明/规则/FAQ 等字段；显式 payload 优先于模板默认值，`None` / 空字符串会触发回填。
- 既有课程草稿创建、更新、详情、列表与 Batch 1~4 回归能力未被破坏。
- targeted 结果：`46 passed in 0.52s`。
- 全量结果：`85 passed in 0.61s`。

## 预期结果
- 满足 B5-TC-003 / B5-TC-004 的最小后端保护：只能从存在且启用中的模板发起建课，且模板默认值可自动回填到课程草稿。
- 模板依赖错误需保持可定位的统一错误码，不允许静默接受失效模板引用。
- 显式传入的课程字段应覆盖模板默认值，避免误改运营手工输入。
- 不破坏既有课程创建主路径与前序 Batch 闭环。

## 自测结论
- 通过

## 已知限制
- 当前已实现模板存在性/启用态保护与模板字段自动回填，但尚未实现复制建课与模板管理写路径。
- 模板来源记录与字段覆盖规则目前仅覆盖创建时默认值回填，后续仍可扩展更细粒度的字段级覆盖策略。

## issue 记录
- Issue ID：无新增批次内阻断 issue；相关范围边界继续受 `B0-ISS-005`、`B0-ISS-004` 跟踪。

### 23.2 验收记录

# 验收记录

- 功能点名称：Batch 5 从模板创建课程 + 模板字段自动回填最小闭环（B5-TC-003 / B5-TC-004）
- 所属 Batch：Batch 5
- 验收角色：QA / Hermes
- 验收日期：2026-04-12
- 验收环境：本地 Python 3.11 + SQLite in-memory
- 验收依据：
  - PRD：`docs/plans/2026-04-11-group-class-kanban-prd.md`
  - 架构设计：`docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
  - 测试文档：`docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
- 关联 issue：`B0-ISS-005`, `B0-ISS-004`

## 验收前提
- Batch 1~4 后端原型回归已稳定通过。
- 当前验收覆盖从模板建课的最小后端保护与模板字段自动回填，不扩大到复制建课或模板管理能力。

## 验收步骤
1. 复核 `create_class_draft()` 在接收 `templateId` 时是否强制检查模板存在性与启用状态。
2. 复核模板缺失、模板停用两条失败路径的错误码是否可区分且符合当前统一错误返回契约。
3. 复核模板默认值自动回填断言，确认字段缺省或为空字符串时会按预期补齐，且显式 payload 仍覆盖模板值。
4. 执行 `source venv/bin/activate && python -m pytest tests/group_class_backend -q` 做回归验收。

## 验收结果
- 结果：通过
- 证据：
  - `apps/group_class_backend/classes/controller.py`
  - `tests/group_class_backend/classes/test_class_queries_and_update.py`
  - `source venv/bin/activate && python -m pytest tests/group_class_backend/classes/test_create_class_draft.py tests/group_class_backend/classes/test_class_queries_and_update.py -q` → `46 passed in 0.52s`
  - `source venv/bin/activate && python -m pytest tests/group_class_backend -q` → `85 passed in 0.61s`
- 是否符合设计：是，已满足 Batch 5 当前阶段对“从模板创建课程必须使用存在且启用模板，且模板默认值可自动回填课程草稿”的最小验收口径。

## 缺陷与偏差
- 尚未实现复制创建课程与模板管理写路径。

## 回归要求
- 后续对 `create_class_draft()`、模板仓储查询、`templateId/template_id` 映射、模板默认值覆盖规则或课程创建参数校验的任何改动，均需回归 `tests/group_class_backend` 全量测试。

## 验收结论
- 通过

## 后续处理建议
- 下一步应优先推进 Batch 5 的复制建课，其次再评估模板管理写路径。