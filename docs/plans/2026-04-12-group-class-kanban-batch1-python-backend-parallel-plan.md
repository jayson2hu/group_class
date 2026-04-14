# 拼课课程系统 Batch 1 Python 后端并行开发计划

Date: 2026-04-12
Status: Ready for execution
Owner: Hermes
Depends on:
- `docs/plans/2026-04-11-group-class-kanban-prd.md`
- `docs/plans/2026-04-11-group-class-kanban-delivery-governance.md`
- `docs/plans/2026-04-11-group-class-kanban-ui-design.md`
- `docs/plans/2026-04-11-group-class-kanban-architecture-design.md`
- `docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md`
- `docs/plans/2026-04-11-group-class-kanban-batch1-field-mapping-and-contract-freeze.md`

> **For Hermes:** 后续执行本计划时，优先使用 `subagent-driven-development` 技能，将任务拆成小功能点逐项实现、自测、验收、记录、审批。

**Goal:** 在 Python 3.11 技术栈下完成 Batch 1 后端最小可运行骨架，使系统具备课程草稿创建、编辑、详情查询、后台列表查询的稳定能力，并为前后端并行开发提供冻结契约。

**Architecture:** 采用单体应用 + 明确模块边界的 Python 后端方案。Batch 1 只落地课程、报名、模板三类核心数据结构与后台课程管理所需最小接口，不提前引入支付、通知、自动状态迁移等增强复杂度。前后端在字段、枚举、错误码、动作集合冻结后并行开发。

**Tech Stack:** Python 3.11、关系型数据库、REST JSON API、ISO 8601 时间格式、统一错误码与审计日志规范。

---

## 1. 文档目的

本计划把现有 PRD、UI、架构、测试文档进一步收敛为 **Batch 1 可执行的 Python 后端并行开发方案**，用于：
1. 指导后端按最小范围稳定实现数据模型与接口骨架。
2. 明确哪些任务可并行、哪些任务必须串行。
3. 为 ACPX / Claude Code / Codex / OpenCode 后续执行提供直接输入。
4. 为 Hermes 的小功能点审批、Batch 审批提供统一检查表。

---

## 2. Batch 1 目标与边界

## 2.1 本批次必须达成
1. `classes` 主实体可创建草稿。
2. `classes` 草稿可编辑、可回填。
3. 后台课程列表接口可返回 UI 所需字段。
4. 后台课程详情接口可返回创建/编辑页所需字段。
5. `registrations`、`class_templates` 完成基础数据结构落地，为后续批次准备依赖。
6. 统一枚举、错误码、响应格式、动作集在代码层有单一来源。
7. 所有 Batch 1 小功能点都有自测记录、验收记录、issue/progress 更新入口。

## 2.2 本批次明确不做
1. 权限细则的完整实现与复杂资源授权。
2. 审核通过 / 驳回 / 发布闭环实现。
3. 前台看板、详情、报名、候补业务接口。
4. 自动状态迁移、支付锁位、通知、导出异步化。
5. 模板管理 UI 与模板批量运营能力。

## 2.3 本批次交付口径
- **后端是主交付对象**：以 Python 后端实现为核心。
- **前端可以并行**：但必须消费冻结契约，不得再自定义字段名。
- **接口可以先完成最小闭环**：即便部分高级校验在 Batch 2 才增强，也不能破坏 Batch 1 契约。

---

## 3. 并行开发前提

开始编码前，以下前提必须满足：
1. `docs/plans/2026-04-11-group-class-kanban-batch1-field-mapping-and-contract-freeze.md` 已评审通过。
2. 课程状态、报名类型、报名状态、课程类型枚举冻结。
3. 后台列表、详情、创建/编辑页字段映射冻结。
4. 通用响应结构、错误响应结构、关键错误码冻结。
5. Batch 1 的 issue log 与 progress 文档已更新。

若以上任一项未完成，Hermes 不批准进入代码实施。

---

## 4. Python 后端建议实现结构

本计划不强制具体 Web 框架，但要求 Python 代码按以下职责边界组织：

### 4.1 推荐模块边界
1. `classes` 模块：课程实体、DTO、仓储、服务、控制器。
2. `registrations` 模块：报名实体、DTO、仓储。
3. `templates` 模块：模板实体、DTO、仓储。
4. `common` 模块：统一枚举、错误码、响应包装、时间与校验工具。
5. `audit` 模块：审计写入接口与日志规范。

### 4.2 代码职责要求
1. **DTO 与持久化模型分离**，避免前端字段直接绑定数据库实现。
2. **写接口走 service 层**，不允许在 controller 中堆业务规则。
3. **枚举和错误码集中定义**，不允许散落硬编码。
4. **返回对象统一 camelCase**，与 API 契约保持一致。
5. **数据库模型字段允许 snake_case**，但映射必须集中管理。

### 4.3 Batch 1 最小持久化对象
1. `Class`
2. `Registration`
3. `ClassTemplate`
4. 可选预留：`ClassReviewRecord`、`ClassStatusHistory` 结构或表占位

---

## 5. Batch 1 任务流拆分

## 5.1 Track A：后端基础设施（串行优先）
1. 建立项目级枚举定义。
2. 建立统一响应包装与错误码定义。
3. 建立基础 ORM / SQL schema / migration 结构。
4. 建立审计接口占位与 `requestId` 透传机制。

## 5.2 Track B：课程数据模型与接口（后端主线）
1. 落地 `classes` 表。
2. 落地课程 DTO 映射。
3. 创建课程草稿接口。
4. 更新课程草稿接口。
5. 获取课程详情接口。
6. 获取课程管理列表接口。

## 5.3 Track C：后续批次依赖对象（可与 Track B 后半段并行）
1. 落地 `registrations` 表基础结构。
2. 落地 `class_templates` 表基础结构。
3. 补齐基础索引、约束、唯一键。

## 5.4 Track D：测试与治理（全程并行）
1. 为每个接口写最小集成测试/契约测试。
2. 记录每个小功能点自测结果。
3. 更新 progress。
4. 更新 issue log。
5. 准备 Hermes 审批输入。

---

## 6. 小功能点执行清单

以下功能点是 **Hermes 审批的最小粒度**。

| 功能点 ID | 名称 | Owner | 依赖 | 可并行性 | 完成定义 |
|---|---|---|---|---|---|
| B1-F01 | 枚举与错误码基线 | Backend | 无 | 否 | 枚举、错误码、通用响应结构落地并测试通过 |
| B1-F02 | `classes` 数据结构 | Backend | B1-F01 | 否 | 表结构、约束、索引完成 |
| B1-F03 | `registrations` 数据结构 | Backend | B1-F01 | 是 | 基础表结构完成，不要求业务流程接入 |
| B1-F04 | `class_templates` 数据结构 | Backend | B1-F01 | 是 | 基础表结构完成，不要求模板管理页接入 |
| B1-F05 | 创建课程草稿接口 | Backend | B1-F02 | 否 | 草稿创建成功并返回标准响应 |
| B1-F06 | 更新课程草稿接口 | Backend | B1-F05 | 否 | 草稿可部分更新并具并发保护 |
| B1-F07 | 课程详情接口 | Backend | B1-F05 | 是 | 编辑页字段可完整回填 |
| B1-F08 | 课程管理列表接口 | Backend | B1-F05 | 是 | 列表字段、分页、动作字段正确 |
| B1-F09 | Batch 1 自测与文档同步 | QA / Hermes | B1-F05~08 | 是 | issue/progress/验收记录更新完成 |

---

## 7. 串行依赖与并行边界

## 7.1 必须串行
1. 完成枚举与错误码冻结，才能写接口返回。
2. 完成 `classes` 数据结构，才能写草稿接口。
3. 创建课程草稿接口跑通后，详情和列表接口才有稳定测试样本。

## 7.2 可并行
1. `registrations` 与 `class_templates` 基础建表可并行。
2. 课程详情接口与课程列表接口可并行。
3. 前端后台页面骨架可与后端接口实现并行推进。
4. 契约测试与自测记录可与功能开发同步编写。

## 7.3 并行注意事项
1. 前端只消费冻结文档中的字段，不允许自创别名。
2. 后端如需新增字段，必须先改冻结文档再编码。
3. 字段语义冲突先登记 issue，再推进修改。
4. 任一接口错误码变化，必须同步前端和测试文档。

---

## 8. Batch 1 API 范围（Python 后端实现清单）

## 8.1 必做接口
1. `GET /api/v1/admin/classes`
2. `GET /api/v1/admin/classes/{classId}`
3. `POST /api/v1/admin/classes`
4. `PUT /api/v1/admin/classes/{classId}`

## 8.2 接口共同要求
1. 返回 `requestId`
2. 返回稳定 `code`
3. 成功时返回 `data`
4. 错误时返回 `details`
5. 后台接口统一鉴权占位
6. 返回 `actions` 字段，前端只做展示控制

## 8.3 Batch 1 最小动作集合
- `view`
- `edit`
- `submit_review`

Batch 1 不强制实现动作判权引擎，但返回口径必须与后续 Batch 2 一致。

---

## 9. 数据模型落地要求

## 9.1 `classes` 必须落地的关键约束
1. `min_students > 0`
2. `max_students >= min_students`
3. `end_date >= start_date`（当日期字段均存在时）
4. `signup_deadline <= start_date`（当字段均存在时）
5. `deposit_amount <= price_amount`（当启用订金时）

## 9.2 `registrations` Batch 1 落地要求
1. 只要求基础结构与索引落地。
2. 不要求开放前台写接口。
3. 必须与 Batch 4 预计字段保持兼容，不得为简化而删减关键字段。

## 9.3 `class_templates` Batch 1 落地要求
1. 只要求基础结构落地。
2. 允许先不接入模板管理 UI。
3. `templateId` 字段在创建课程草稿接口中可为空。

---

## 10. 校验与错误处理要求

## 10.1 草稿保存校验
1. 草稿允许部分字段为空。
2. 至少满足 `className` 或 `templateId` 之一。
3. 非完整字段不应触发发布级校验。

## 10.2 标准错误码要求
Batch 1 至少支持：
1. `VALIDATION_INVALID_ARGUMENT`
2. `VALIDATION_REQUIRED_FIELD_MISSING`
3. `CLASS_NOT_FOUND`
4. `CLASS_VERSION_CONFLICT`
5. `PERMISSION_DENIED`
6. `SYSTEM_INTERNAL_ERROR`

## 10.3 Batch 1 错误处理原则
1. 字段错误就近返回字段级 `details`。
2. 版本冲突返回明确错误码，前端可提示刷新。
3. 任何 5xx 必须打应用日志并带 `requestId`。

---

## 11. 测试与验收要求

## 11.1 每个小功能点必须提交的证据
1. 代码变更文件清单
2. 自测命令与结果
3. 验收结论
4. issue log 更新项
5. progress 更新项
6. Hermes 审批结论

## 11.2 Batch 1 最小测试集
1. 数据模型约束测试
2. 草稿创建成功测试
3. 草稿部分更新测试
4. 详情回填测试
5. 列表字段映射测试
6. 标准错误响应测试
7. 版本冲突测试

## 11.3 验收通过标准
1. 后台可成功创建课程草稿。
2. 后台详情接口可完整回填创建页字段。
3. 后台列表接口字段与 UI 设计一致。
4. 错误码与响应结构符合冻结契约。
5. `registrations` / `class_templates` 基础结构已落地。
6. progress 与 issue log 已同步。

---

## 12. ACPX / 代理执行建议

## 12.1 推荐执行方式
- 子任务 1：后端枚举、错误码、响应封装
- 子任务 2：`classes` 数据结构与 migration
- 子任务 3：草稿创建 / 更新 / 详情接口
- 子任务 4：列表接口 + 测试 + 文档同步
- 子任务 5：`registrations` / `class_templates` 基础建表

## 12.2 代理提示词模板
```text
阅读以下文档并仅执行 Batch 1 Python 后端范围：
- docs/plans/2026-04-11-group-class-kanban-prd.md
- docs/plans/2026-04-11-group-class-kanban-ui-design.md
- docs/plans/2026-04-11-group-class-kanban-architecture-design.md
- docs/plans/2026-04-11-group-class-kanban-test-and-acceptance.md
- docs/plans/2026-04-11-group-class-kanban-batch1-field-mapping-and-contract-freeze.md
- docs/plans/2026-04-12-group-class-kanban-batch1-python-backend-parallel-plan.md

要求：
1. 仅做 Python 后端 Batch 1 最小闭环。
2. 严格按小功能点推进。
3. 每完成一个小功能点，必须先自测再更新文档。
4. 不得擅自修改冻结字段、错误码、响应结构。
5. 输出修改文件清单、测试结果、未解决问题、待 Hermes 审批项。
```

---

## 13. 风险与防返工规则

1. 如果接口字段名、枚举名、错误码名与冻结文档不一致，视为未完成。
2. 如果前端页面字段无法直接映射到接口返回，必须先修正文档或接口，不允许前端写临时转换口径。
3. 如果 Batch 1 引入 Batch 2/3/4 的业务复杂度，Hermes 有权驳回变更。
4. 如果未更新 progress 或 issue log，不得标记完成。

---

## 14. Hermes 审批清单

Hermes 审批 Batch 1 前，逐项确认：
1. 小功能点是否独立闭环。
2. 数据模型、接口、测试是否覆盖 Batch 1 范围。
3. 文档与代码是否一致。
4. 是否存在未登记的契约变更。
5. 是否仍保留可并行推进的稳定边界。

---

## 15. 当前结论

Batch 1 已具备进入 **Python 后端并行开发** 的文档前提，但执行前必须以字段映射与契约冻结文档为唯一标准源。若后续框架选型（FastAPI / Django / Flask 等）发生变化，不影响本计划；实现层可变，但契约层不得漂移。
