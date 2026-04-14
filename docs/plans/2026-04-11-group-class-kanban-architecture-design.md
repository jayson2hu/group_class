# 拼课课程系统 Batch 0 后端/架构设计文档

Date: 2026-04-11  
Status: Draft for Design Review  
Role: Architect  
Owner: Hermes  
Depends on:
- `docs/plans/2026-04-11-group-class-kanban-prd.md`
- `docs/plans/2026-04-11-group-class-kanban-delivery-governance.md`
- `docs/plans/2026-04-11-group-class-kanban-ui-design.md`
- `docs/plans/2026-04-11-group-class-kanban-acpx-implementation-plan.md`

---

## 1. 文档目标

本文档用于完成 Batch 0 的后端与架构设计冻结，给后续 Batch 1 至 Batch 4 的实现提供统一的系统边界、领域模型、权限模型、状态机、数据结构与 API 契约基础。

本文档目标不是直接交付业务功能，而是完成以下事项：
1. 明确系统目标与设计原则
2. 冻结并行开发所需的关键契约
3. 定义模块边界与职责归属
4. 明确角色权限与状态流转
5. 产出可实现的数据模型与 API 合同
6. 给出日志审计、异常处理与非功能约束
7. 标记哪些工作可并行，哪些必须串行
8. 形成设计评审结论与待确认事项

---

## 2. Batch 0 范围与非范围

### 2.1 Batch 0 范围
Batch 0 仅完成设计与治理初始化，不直接上线业务功能代码。输出内容包括：
1. 后端总体架构设计
2. 模块划分与服务边界
3. 核心领域模型
4. 角色与权限模型
5. 课程状态机与报名状态定义
6. 关键数据表设计
7. API 契约草案与冻结项
8. 审计、日志、错误处理规范
9. 非功能需求基线
10. 并行开发与串行依赖说明
11. 设计评审结论与开放问题

### 2.2 本文档支撑的后续批次
1. Batch 1：数据模型与后台课程管理骨架
2. Batch 2：角色权限与审核发布流
3. Batch 3：前台课程看板与详情页
4. Batch 4：报名、候补、报名管理

### 2.3 本文档不覆盖
1. 支付锁位
2. 自动通知
3. 自动高级状态机
4. CRM 深度打通
5. 智能推荐与 BI 分析
6. 模板高级权限与多版本管理

---

## 3. 设计目标

### 3.1 业务目标
1. 替代微信群接龙，形成统一课程供给与报名入口
2. 支持管理员与指定发起人的受控建课流程
3. 支持课程审核与发布，保证前台只展示有效课程
4. 支持结构化报名、候补、试听意向留资
5. 支持运营跟踪课程状态、人数、负责人和报名数据

### 3.2 技术目标
1. 用最小复杂度支持 P0 范围
2. 设计上兼容后续支付、通知、自动化能力扩展
3. 保证前后端在冻结契约下可并行开发
4. 保证状态、权限、审计链路可追踪
5. 保证关键业务动作可验证、可回放、可排错

---

## 4. 架构原则

### 4.1 单体优先，边界清晰
P0-P1 阶段采用单体应用架构，不拆分微服务；通过模块边界、领域对象和接口契约保证后续可演进。

### 4.2 先建模再编码
所有实现必须以冻结的领域模型、状态机、权限矩阵和 API 合同为准，不允许前后端各自发明字段和状态。

### 4.3 写路径强约束，读路径轻聚合
创建课程、提交审核、审核、发布、报名、候补等写操作必须经过明确命令路径与校验；列表页、详情页等读接口允许做只读聚合。

### 4.4 显式状态，不做隐式魔法
课程状态与报名状态必须显式存储；自动派生规则可作为辅助计算存在，但不能替代可审计的业务状态字段。

### 4.5 权限前置，审计默认开启
所有后台写接口默认需要角色与资源级校验；关键动作必须产生日志和审计记录。

### 4.6 兼容演进
数据模型和 API 设计为后续能力预留扩展位，但不提前引入复杂工作流引擎、事件总线或多租户模型。

---

## 5. 系统上下文

### 5.1 参与方
1. 普通用户：查看课程、报名、候补、试听申请
2. 指定发起人：创建课程草稿、提交审核、查看自己课程报名情况
3. 课程管理员：管理课程、审核、发布、查看报名
4. 超级管理员：平台级管理、角色配置、模板配置、全量数据查看
5. 运营/老师：作为课程负责人进行跟进
6. Hermes：设计与交付审批者，不属于运行时系统角色

### 5.2 系统边界
本系统负责：
1. 课程供给管理
2. 课程展示
3. 报名留资
4. 审核发布
5. 人数与状态管理
6. 审计与后台管理

本系统暂不负责：
1. 真实支付交易
2. 外部消息通知发送
3. CRM 主数据管理
4. 教务正式排课

### 5.3 外部依赖
P0 默认可独立运行。若有外部系统，先按可选集成处理：
1. 认证源：现有后台用户体系或平台账号体系
2. 文件存储：课程封面上传
3. 导出能力：CSV/Excel 生成
4. 消息系统：后续批次再接

---

## 6. 总体架构

### 6.1 推荐架构
采用“前后台一体应用 + 关系型数据库 + 对象存储”的单体分层架构。

分层如下：
1. 展示层
   - 前台用户端页面
   - 后台管理端页面
2. 接口层
   - REST API
   - 统一鉴权与错误返回
3. 应用层
   - 课程管理应用服务
   - 审核发布应用服务
   - 报名管理应用服务
   - 权限与审计应用服务
4. 领域层
   - 课程聚合
   - 报名聚合
   - 模板聚合
   - 状态机与领域规则
5. 基础设施层
   - MySQL/PostgreSQL
   - Redis 可选
   - 文件存储
   - 审计日志存储
   - 后台导出任务

### 6.2 架构风格说明
1. P0-P1 以同步接口为主
2. 导出、审计归档等可异步
3. 状态计算优先在应用层完成
4. 不引入分布式事务
5. 所有关键状态变更在数据库事务内完成

---

## 7. 模块边界

## 7.1 账户与身份模块
职责：
1. 识别当前用户
2. 返回角色集合
3. 提供用户基础信息用于创建人、负责人、审核人关联

不负责：
1. 复杂组织架构
2. 外部 SSO 编排逻辑

## 7.2 课程管理模块
职责：
1. 创建课程草稿
2. 编辑课程
3. 保存草稿
4. 查看课程列表与详情
5. 维护课程负责人、模板来源、展示文案

边界：
1. 不直接处理支付
2. 不负责消息通知发送

## 7.3 审核发布模块
职责：
1. 提交审核
2. 审核通过
3. 审核驳回
4. 发布、下架、取消
5. 维护课程审核记录与状态流转记录

边界：
1. 仅负责课程生命周期控制
2. 不处理报名详情编辑

## 7.4 报名管理模块
职责：
1. 提交报名
2. 提交候补
3. 提交试听意向
4. 查看报名列表与详情
5. 标记有效/无效
6. 跟进备注

> Execution Update (2026-04-12): 当前原型已完成公开报名/候补提交、后台报名列表读取、报名详情回显、跟进备注更新、报名状态更新（`VALID` / `INVALID` / `CANCELLED`）、课程人数快照更新、审计落库与 SQLite 持久化基线；其中后台报名读取/写入能力已支持 `CLASS_ADMIN` / `SUPER_ADMIN` 查看与更新全部报名、`INITIATOR` 仅操作自己创建课程的报名记录。下一阶段主要剩余更细粒度的资源范围配置，以及导出名单等运营增强能力。

边界：
1. 不负责支付
2. 不负责自动转正
3. 不负责 CRM 推送

## 7.5 模板模块
职责：
1. 提供模板字段预填
2. 记录模板来源
3. 支撑“从模板创建课程”

> Execution Update (2026-04-12): 当前原型已完成 Batch 5 `B5-TC-003` 的最小后端保护：`create_class_draft` 仅允许使用存在且启用中的模板创建课程；模板不存在时返回 `CLASS_NOT_FOUND`，模板停用时返回 `VALIDATION_INVALID_ARGUMENT`。该实现目前只覆盖模板存在性与启用态校验，模板字段自动回填、复制建课与模板管理写路径仍待后续 Batch 5 子功能继续补齐。

边界：
1. P0 仅定义基础数据结构和引用关系
2. 模板后台管理页在后续批次增强

## 7.6 审计与日志模块
职责：
1. 记录关键操作日志
2. 记录状态变更历史
3. 记录异常与系统事件
4. 支撑追溯、排错与验收

---

## 8. 领域模型

## 8.1 核心聚合
1. 课程聚合 `Class`
2. 报名聚合 `Registration`
3. 模板聚合 `ClassTemplate`
4. 审核记录 `ClassReviewRecord`
5. 状态变更记录 `ClassStatusHistory`
6. 操作审计记录 `AuditLog`

### 8.2 聚合关系
1. 一个课程可关联零个或一个模板
2. 一个课程可有多个报名记录
3. 一个课程可有多条审核记录
4. 一个课程可有多条状态变更记录
5. 一个用户可创建多个课程
6. 一个用户可负责多个课程

### 8.3 聚合根定义
1. `Class` 为课程相关写操作聚合根
2. `Registration` 为报名相关写操作聚合根
3. 审核记录与状态历史由课程聚合驱动产生，不允许独立修改

---

## 9. 角色与权限模型

## 9.1 角色枚举
1. `SUPER_ADMIN`
2. `CLASS_ADMIN`
3. `INITIATOR`
4. `USER`

### 9.2 权限原则
1. 后台权限基于角色 + 资源归属联合判断
2. 前台公开读接口不依赖登录，若后续需要留资防刷再加校验
3. 同一用户可拥有多个角色，按并集授权
4. 资源归属包含创建人、负责人、审核责任范围

### 9.3 权限矩阵

| 动作 | 超级管理员 | 课程管理员 | 指定发起人 | 普通用户 |
|---|---|---|---|---|
| 查看前台课程 | 是 | 是 | 是 | 是 |
| 提交报名/候补/试听 | 是 | 是 | 是 | 是 |
| 查看后台课程列表 | 是 | 是 | 仅自己 | 否 |
| 创建课程草稿 | 是 | 是 | 是 | 否 |
| 编辑草稿 | 是 | 自己负责/有权限范围 | 自己创建 | 否 |
| 提交审核 | 是 | 是 | 是 | 否 |
| 审核通过/驳回 | 是 | 是，可按配置限制 | 否 | 否 |
| 直接发布课程 | 是 | 可配置 | 否 | 否 |
| 下架/取消课程 | 是 | 自己负责/有权限范围 | 否 | 否 |
| 查看报名数据 | 全部 | 自己负责/有权限范围 | 自己发起课程 | 否 |
| 导出报名名单 | 是 | 是 | 否 | 否 |
| 配置角色权限 | 是 | 否 | 否 | 否 |
| 管理模板 | 是 | 是 | 只可使用 | 否 |

### 9.4 资源级规则
1. `INITIATOR` 只能编辑自己创建且未进入不可编辑终态的课程
2. `CLASS_ADMIN` 默认可操作自己负责课程；是否可审核全部课程由配置决定
3. `SUPER_ADMIN` 不受资源归属限制
4. 报名数据查询必须按课程权限过滤

### 9.5 前端权限返回方式
冻结方案：
1. 登录后后台接口返回当前用户角色集
2. 课程详情和课程列表接口返回 `actions` 字段，显式告诉前端可执行动作
3. 前端只做展示控制，后端做最终强校验

示例：
```json
{
  "roleCodes": ["CLASS_ADMIN"],
  "actions": ["view", "edit", "submit_review", "publish"]
}
```

---

## 10. 状态机设计

## 10.1 课程状态枚举
冻结枚举如下：
1. `DRAFT` 草稿
2. `PENDING_REVIEW` 待审核
3. `OPEN_FOR_ENROLLMENT` 报名中
4. `ALMOST_CONFIRMED` 即将成班
5. `CONFIRMED` 已成班
6. `IN_PROGRESS` 进行中
7. `FULL` 已满员
8. `WAITLIST_OPEN` 候补中
9. `ENDED` 已结束
10. `CANCELLED` 已取消
11. `REJECTED` 已驳回内部态，仅后台可见

说明：
1. PRD 文案中“驳回 -> 草稿”是业务体验要求
2. 数据层建议保留 `REJECTED` 中间态用于审计与历史回看
3. 前台永不展示 `DRAFT`、`PENDING_REVIEW`、`REJECTED`

## 10.2 报名类型枚举
1. `ENROLLMENT` 正式报名
2. `WAITLIST` 候补登记
3. `TRIAL` 试听申请

## 10.3 报名状态枚举
1. `SUBMITTED` 已提交
2. `VALID` 有效
3. `INVALID` 无效
4. `WAITLISTED` 已候补
5. `TRANSFERRED` 已转班
6. `CANCELLED` 已取消

## 10.4 课程状态流转

### 10.4.1 人工主流程
1. `DRAFT -> PENDING_REVIEW`
2. `PENDING_REVIEW -> OPEN_FOR_ENROLLMENT`
3. `PENDING_REVIEW -> REJECTED`
4. `REJECTED -> DRAFT`
5. `OPEN_FOR_ENROLLMENT -> CANCELLED`
6. `OPEN_FOR_ENROLLMENT -> WAITLIST_OPEN`
7. `OPEN_FOR_ENROLLMENT -> FULL`
8. `OPEN_FOR_ENROLLMENT -> IN_PROGRESS`
9. `ALMOST_CONFIRMED -> CONFIRMED`
10. `CONFIRMED -> FULL`
11. `CONFIRMED -> IN_PROGRESS`
12. `IN_PROGRESS -> ENDED`
13. `FULL -> WAITLIST_OPEN`
14. `FULL -> IN_PROGRESS`
15. `WAITLIST_OPEN -> IN_PROGRESS`
16. `WAITLIST_OPEN -> CANCELLED`

### 10.4.2 派生显示规则
以下状态可由人数和时间辅助计算并建议刷新，但不替代主状态字段：
1. `OPEN_FOR_ENROLLMENT` 且 `current_students >= ceil(min_students * 0.6)` 时，前台可显示 `ALMOST_CONFIRMED`
2. `current_students >= min_students` 时，允许进入 `CONFIRMED`
3. `current_students >= max_students` 时，允许进入 `FULL`
4. `start_date <= today` 时，允许进入 `IN_PROGRESS`

### 10.4.3 Batch 0 冻结原则
1. Batch 1/2 先按显式状态实现
2. 自动状态迁移不在本批次落地
3. 可提供后台手动调整或发布逻辑中带校验
4. 后续自动化任务只是在冻结状态机上补充自动触发器

## 10.5 状态变更约束
1. 只有通过审核的课程才能进入前台可见状态
2. 已取消课程不可再恢复为报名中，需复制创建新课
3. 已结束课程不可编辑核心字段
4. 已满员课程前台主 CTA 变更为候补
5. 驳回必须填写理由
6. 发布前必须通过完整校验

---

## 11. 数据模型设计

## 11.1 设计原则
1. 采用关系型数据库
2. 关键字段保留明确业务含义
3. 状态与计数字段落库，避免高频临时聚合
4. 长文本与 FAQ 使用 JSON 或 text 字段
5. 审计和历史记录独立表存储

## 11.2 表：`classes`
用途：存储课程主实体。

| 字段 | 类型建议 | 必填 | 说明 |
|---|---|---|---|
| id | bigint / uuid | 是 | 主键 |
| class_code | varchar(32) | 是 | 业务编码，便于追踪 |
| class_name | varchar(128) | 是 | 课程名称 |
| class_subtitle | varchar(255) | 否 | 副标题 |
| class_type | varchar(32) | 是 | `GROUP_CLASS`/`TRIAL_CLASS`/`REGULAR_CLASS` |
| target_group | varchar(128) | 否 | 目标人群摘要 |
| suitable_for | text | 否 | 适合对象 |
| not_suitable_for | text | 否 | 不适合对象 |
| class_desc | text | 否 | 课程简介/说明 |
| course_goals | text | 否 | 课程目标 |
| class_highlights | text | 否 | 课程亮点 |
| class_notice | text | 否 | 补充说明 |
| faq_json | json | 否 | FAQ 列表 |
| banner_image_url | varchar(512) | 否 | 课程封面 |
| schedule_time | varchar(128) | 是 | 上课时间展示文案 |
| lesson_duration_minutes | int | 否 | 每次时长 |
| start_date | date | 是 | 开课日期 |
| end_date | date | 是 | 结束日期 |
| total_lessons | int | 是 | 总课次 |
| signup_deadline | datetime | 是 | 报名截止时间 |
| price_amount | decimal(10,2) | 是 | 价格 |
| deposit_enabled | boolean | 是 | 是否支持订金 |
| deposit_amount | decimal(10,2) | 否 | 订金金额 |
| payment_notice | text | 否 | 支付说明 |
| min_students | int | 是 | 最低成班人数 |
| max_students | int | 是 | 最大人数 |
| current_students | int | 是 | 当前有效报名人数快照 |
| waitlist_count | int | 是 | 候补人数快照 |
| allow_waitlist | boolean | 是 | 是否允许候补 |
| allow_trial | boolean | 是 | 是否允许试听 |
| allow_transfer | boolean | 是 | 是否支持调班 |
| allow_mid_join | boolean | 是 | 是否支持插班 |
| fail_to_launch_policy | varchar(32) | 是 | `AUTO_CANCEL`/`MANUAL_HANDLE`/`DEFER`/`RECOMMEND_OTHER` |
| status | varchar(32) | 是 | 课程状态 |
| creator_id | bigint / uuid | 是 | 创建人 |
| owner_id | bigint / uuid | 否 | 负责人 |
| reviewer_id | bigint / uuid | 否 | 最近审核人 |
| template_id | bigint / uuid | 否 | 模板来源 |
| latest_review_comment | text | 否 | 最近审核意见摘要 |
| published_at | datetime | 否 | 发布时间 |
| cancelled_at | datetime | 否 | 取消时间 |
| created_at | datetime | 是 | 创建时间 |
| updated_at | datetime | 是 | 更新时间 |
| deleted_at | datetime | 否 | 软删除时间 |

约束：
1. `min_students > 0`
2. `max_students >= min_students`
3. `end_date >= start_date`
4. `signup_deadline <= start_date`
5. `deposit_amount <= price_amount` 当 `deposit_enabled=true`

索引建议：
1. `idx_classes_status_created_at`
2. `idx_classes_creator_id_status`
3. `idx_classes_owner_id_status`
4. `idx_classes_signup_deadline`
5. `idx_classes_start_date`
6. `uk_classes_class_code`

## 11.3 表：`registrations`
用途：存储报名、候补、试听意向记录。

| 字段 | 类型建议 | 必填 | 说明 |
|---|---|---|---|
| id | bigint / uuid | 是 | 主键 |
| registration_code | varchar(32) | 是 | 业务编码 |
| class_id | bigint / uuid | 是 | 课程 ID |
| register_type | varchar(32) | 是 | 报名类型 |
| registration_status | varchar(32) | 是 | 报名状态 |
| parent_name | varchar(64) | 是 | 家长姓名/联系人 |
| contact_info | varchar(64) | 是 | 手机号或联系方式 |
| student_name | varchar(64) | 否 | 学员姓名，候补可选 |
| student_grade | varchar(32) | 是 | 学员年级 |
| english_level | varchar(64) | 否 | 英语基础 |
| accept_transfer | boolean | 否 | 是否接受调班 |
| accept_waitlist | boolean | 否 | 是否接受候补 |
| wants_trial | boolean | 否 | 是否想试听 |
| accept_similar_recommendation | boolean | 否 | 是否接受相近课程推荐 |
| remark | text | 否 | 用户备注 |
| follow_up_note | text | 否 | 运营跟进备注 |
| payment_status | varchar(32) | 否 | 预留字段 |
| submitted_ip | varchar(64) | 否 | 风控预留 |
| submitted_user_agent | varchar(255) | 否 | 风控预留 |
| created_at | datetime | 是 | 创建时间 |
| updated_at | datetime | 是 | 更新时间 |

约束：
1. `register_type=ENROLLMENT` 时，`student_name`、`english_level`、`accept_waitlist` 可用
2. `register_type=WAITLIST` 时，允许字段更轻量
3. `register_type=TRIAL` 时，试听相关字段可选

索引建议：
1. `idx_registrations_class_id_created_at`
2. `idx_registrations_type_status`
3. `idx_registrations_contact_info`
4. `uk_registrations_registration_code`

## 11.4 表：`class_templates`
用途：存储课程模板。

| 字段 | 类型建议 | 必填 | 说明 |
|---|---|---|---|
| id | bigint / uuid | 是 | 主键 |
| template_name | varchar(128) | 是 | 模板名称 |
| class_type | varchar(32) | 是 | 默认课程类型 |
| default_class_name_pattern | varchar(255) | 否 | 默认名称模板 |
| default_suitable_for | text | 否 | 默认适合对象 |
| default_price_amount | decimal(10,2) | 否 | 默认价格 |
| default_min_students | int | 否 | 默认成班人数 |
| default_max_students | int | 否 | 默认满班人数 |
| default_faq_json | json | 否 | 默认 FAQ |
| default_class_notice | text | 否 | 默认课程说明 |
| enabled | boolean | 是 | 是否启用 |
| created_by | bigint / uuid | 是 | 创建人 |
| created_at | datetime | 是 | 创建时间 |
| updated_at | datetime | 是 | 更新时间 |

## 11.5 表：`class_review_records`
用途：存储课程审核记录。

| 字段 | 类型建议 | 必填 | 说明 |
|---|---|---|---|
| id | bigint / uuid | 是 | 主键 |
| class_id | bigint / uuid | 是 | 课程 ID |
| action | varchar(32) | 是 | `SUBMIT`/`APPROVE`/`REJECT`/`PUBLISH` |
| from_status | varchar(32) | 是 | 原状态 |
| to_status | varchar(32) | 是 | 目标状态 |
| reviewer_id | bigint / uuid | 否 | 审核人 |
| comment | text | 否 | 审核意见 |
| created_at | datetime | 是 | 操作时间 |

索引建议：
1. `idx_review_records_class_id_created_at`

## 11.6 表：`class_status_histories`
用途：存储课程状态变更历史。

| 字段 | 类型建议 | 必填 | 说明 |
|---|---|---|---|
| id | bigint / uuid | 是 | 主键 |
| class_id | bigint / uuid | 是 | 课程 ID |
| from_status | varchar(32) | 否 | 原状态 |
| to_status | varchar(32) | 是 | 新状态 |
| reason_code | varchar(32) | 否 | 原因码 |
| reason_text | text | 否 | 原因文本 |
| operator_id | bigint / uuid | 否 | 操作人 |
| created_at | datetime | 是 | 变更时间 |

## 11.7 表：`audit_logs`
用途：记录关键操作审计。

| 字段 | 类型建议 | 必填 | 说明 |
|---|---|---|---|
| id | bigint / uuid | 是 | 主键 |
| actor_id | bigint / uuid | 否 | 操作人 |
| actor_roles | varchar(255) | 否 | 角色快照 |
| entity_type | varchar(64) | 是 | `CLASS`/`REGISTRATION`/`TEMPLATE` |
| entity_id | varchar(64) | 是 | 实体 ID |
| action | varchar(64) | 是 | 操作动作 |
| request_id | varchar(64) | 否 | 请求链路 ID |
| before_snapshot | json | 否 | 变更前快照 |
| after_snapshot | json | 否 | 变更后快照 |
| result | varchar(16) | 是 | `SUCCESS`/`FAIL` |
| error_code | varchar(64) | 否 | 错误码 |
| metadata_json | json | 否 | 扩展信息 |
| created_at | datetime | 是 | 记录时间 |

---

## 12. 数据一致性与事务策略

### 12.1 一致性原则
1. 单次命令只更新一个聚合根及其附属历史
2. 课程状态变更与状态历史写入必须同事务
3. 报名创建与课程计数更新必须同事务
4. 审核通过与发布时间写入必须同事务

### 12.2 计数字段策略
`current_students` 与 `waitlist_count` 采用写时维护快照，避免列表页实时聚合压力。

更新规则：
1. 新增有效正式报名时 `current_students + 1`
2. 正式报名转无效或取消时 `current_students - 1`
3. 新增候补时 `waitlist_count + 1`
4. 候补取消时 `waitlist_count - 1`

### 12.3 并发控制
1. 课程更新接口采用乐观锁字段 `version` 或 `updated_at` 防覆盖
2. 报名提交时对课程记录加行级锁，防止超卖
3. 当达到 `max_students` 时，正式报名接口返回满员错误，引导用户走候补

---

## 13. API 契约设计

## 13.1 设计约定
1. 风格：REST
2. 传输：JSON
3. 时间：ISO 8601
4. ID：字符串输出，避免前端精度问题
5. 所有响应包含 `requestId`
6. 所有后台接口必须鉴权
7. 所有写接口必须返回最新状态摘要

统一响应建议：
```json
{
  "requestId": "req_20260411_xxx",
  "code": "OK",
  "message": "success",
  "data": {}
}
```

错误响应建议：
```json
{
  "requestId": "req_20260411_xxx",
  "code": "CLASS_STATUS_INVALID",
  "message": "当前课程状态不允许执行该操作",
  "details": {}
}
```

## 13.2 冻结枚举契约
前后端必须先冻结以下枚举：
1. 课程状态枚举
2. 报名类型枚举
3. 报名状态枚举
4. 课程类型枚举
5. 不成班处理方式枚举
6. 权限动作枚举

## 13.3 前台接口

### 13.3.1 获取课程看板列表
`GET /api/v1/public/classes`

查询参数：
- `status[]` 可选
- `grade` 可选，P1 预留
- `timeSlot` 可选，P1 预留

返回字段：
```json
{
  "items": [
    {
      "id": "cls_001",
      "className": "三年级英语拼课班",
      "classSubtitle": "晚间启蒙小班",
      "targetGroup": "三年级",
      "scheduleTime": "每周三 19:00-20:30",
      "startDate": "2026-04-20",
      "endDate": "2026-06-20",
      "totalLessons": 12,
      "priceAmount": 1999,
      "currentStudents": 4,
      "minStudents": 6,
      "maxStudents": 8,
      "status": "ALMOST_CONFIRMED",
      "statusLabel": "即将成班",
      "progressText": "还差 2 人成班",
      "allowWaitlist": true,
      "allowTrial": true,
      "actions": ["view_detail", "enroll", "trial"]
    }
  ]
}
```

规则：
1. 只返回前台可见状态
2. 默认不返回已取消、已结束、草稿、待审核、驳回课程

### 13.3.2 获取课程详情
`GET /api/v1/public/classes/{classId}`

返回字段应覆盖 UI 详情页所需：
```json
{
  "id": "cls_001",
  "className": "三年级英语拼课班",
  "classSubtitle": "晚间启蒙小班",
  "status": "ALMOST_CONFIRMED",
  "statusLabel": "即将成班",
  "currentStudents": 4,
  "minStudents": 6,
  "maxStudents": 8,
  "priceAmount": 1999,
  "scheduleTime": "每周三 19:00-20:30",
  "startDate": "2026-04-20",
  "endDate": "2026-06-20",
  "suitableFor": "三年级英语基础薄弱学生",
  "notSuitableFor": "已具备完整语法基础学生",
  "courseGoals": "提升阅读与口语基础",
  "classHighlights": "小班互动、作业反馈",
  "classNotice": "报名后由老师联系",
  "faq": [
    {
      "question": "不成班怎么办？",
      "answer": "将按课程规则处理"
    }
  ],
  "rules": {
    "allowWaitlist": true,
    "allowTrial": true,
    "allowTransfer": true,
    "allowMidJoin": false,
    "failToLaunchPolicy": "MANUAL_HANDLE"
  },
  "actions": ["enroll", "trial"]
}
```

### 13.3.3 提交报名
`POST /api/v1/public/registrations`

请求体：
```json
{
  "classId": "cls_001",
  "registerType": "ENROLLMENT",
  "parentName": "张女士",
  "contactInfo": "13800000000",
  "studentName": "张三",
  "studentGrade": "三年级",
  "englishLevel": "基础一般",
  "acceptTransfer": true,
  "acceptWaitlist": true,
  "wantsTrial": false,
  "remark": "希望同校同学一起"
}
```

返回：
```json
{
  "registrationId": "reg_001",
  "registerType": "ENROLLMENT",
  "registrationStatus": "SUBMITTED",
  "classStatus": "ALMOST_CONFIRMED",
  "nextStepText": "提交成功，老师/运营将尽快联系确认"
}
```

### 13.3.4 提交候补
`POST /api/v1/public/waitlist-registrations`

请求体：
```json
{
  "classId": "cls_001",
  "registerType": "WAITLIST",
  "parentName": "李女士",
  "contactInfo": "13900000000",
  "studentGrade": "四年级",
  "acceptSimilarRecommendation": true,
  "remark": "可接受相近时间段"
}
```

### 13.3.5 提交试听申请
`POST /api/v1/public/trial-registrations`

说明：
1. 也可统一复用报名接口，通过 `registerType=TRIAL`
2. Batch 0 冻结建议是后端统一一个报名写接口，前端按场景封装
3. 实现阶段对外可保留单接口，减少后台逻辑分叉

## 13.4 后台课程接口

### 13.4.1 获取课程管理列表
`GET /api/v1/admin/classes`

查询参数：
- `status`
- `creatorId`
- `ownerId`
- `classType`
- `dateFrom`
- `dateTo`
- `page`
- `pageSize`

返回字段：
```json
{
  "items": [
    {
      "id": "cls_001",
      "className": "三年级英语拼课班",
      "classType": "GROUP_CLASS",
      "targetGroup": "三年级",
      "scheduleTime": "每周三 19:00-20:30",
      "currentStudents": 4,
      "minStudents": 6,
      "maxStudents": 8,
      "status": "DRAFT",
      "creator": {
        "id": "u_001",
        "name": "老师A"
      },
      "owner": {
        "id": "u_002",
        "name": "运营B"
      },
      "signupDeadline": "2026-04-18T23:59:59+08:00",
      "createdAt": "2026-04-11T10:00:00+08:00",
      "actions": ["view", "edit", "submit_review"]
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 1
  }
}
```

### 13.4.2 获取课程详情
`GET /api/v1/admin/classes/{classId}`

要求：
1. 返回所有编辑页字段
2. 返回当前状态与可操作动作
3. 返回最近审核记录摘要

### 13.4.3 创建课程草稿
`POST /api/v1/admin/classes`

请求体：
```json
{
  "className": "三年级英语拼课班",
  "classSubtitle": "晚间启蒙小班",
  "classType": "GROUP_CLASS",
  "suitableFor": "三年级英语基础薄弱学生",
  "notSuitableFor": "高阶语法强化学生",
  "classDesc": "课程简介",
  "scheduleTime": "每周三 19:00-20:30",
  "lessonDurationMinutes": 90,
  "startDate": "2026-04-20",
  "endDate": "2026-06-20",
  "totalLessons": 12,
  "signupDeadline": "2026-04-18T23:59:59+08:00",
  "minStudents": 6,
  "maxStudents": 8,
  "allowWaitlist": true,
  "allowTrial": true,
  "allowTransfer": true,
  "allowMidJoin": false,
  "failToLaunchPolicy": "MANUAL_HANDLE",
  "priceAmount": 1999,
  "depositEnabled": false,
  "courseGoals": "提升阅读与口语基础",
  "classHighlights": "小班互动",
  "classNotice": "报名后联系确认",
  "faq": [],
  "ownerId": "u_002",
  "templateId": "tpl_001"
}
```

返回：
1. 课程 ID
2. 当前状态 `DRAFT`
3. 草稿保存时间

### 13.4.4 更新课程草稿
`PUT /api/v1/admin/classes/{classId}`

规则：
1. 草稿允许部分字段保存
2. 发布前校验与草稿保存校验不同
3. 需带版本号或更新时间做并发控制

### 13.4.5 提交审核
`POST /api/v1/admin/classes/{classId}/submit-review`

规则：
1. 仅 `DRAFT` 或 `REJECTED` 可提交
2. 提交前执行必填校验
3. 写入审核记录与状态历史

### 13.4.6 审核通过
`POST /api/v1/admin/classes/{classId}/approve`

规则：
1. 仅有审核权限角色可调用
2. 仅 `PENDING_REVIEW` 可通过
3. 默认流转到 `OPEN_FOR_ENROLLMENT`
4. 可同时设置 `publishedAt`

### 13.4.7 审核驳回
`POST /api/v1/admin/classes/{classId}/reject`

请求体：
```json
{
  "comment": "课程时间与说明不完整，请补充"
}
```

规则：
1. 驳回意见必填
2. 状态进入 `REJECTED`
3. 前端编辑页收到后应引导回草稿态继续编辑

### 13.4.8 发布课程
`POST /api/v1/admin/classes/{classId}/publish`

规则：
1. 超级管理员可直接发布
2. 课程管理员是否可直接发布由平台配置决定
3. 指定发起人不可直接发布
4. 若课程已审核通过且未发布，可进入 `OPEN_FOR_ENROLLMENT`

### 13.4.9 下架/取消课程
`POST /api/v1/admin/classes/{classId}/cancel`

请求体：
```json
{
  "reasonCode": "MANUAL_CANCEL",
  "reasonText": "招生计划变更"
}
```

## 13.5 后台报名接口

### 13.5.1 获取报名列表
`GET /api/v1/admin/registrations`

查询参数：
- `classId`
- `registerType`
- `registrationStatus`
- `dateFrom`
- `dateTo`
- `page`
- `pageSize`

### 13.5.2 获取报名详情
`GET /api/v1/admin/registrations/{registrationId}`

### 13.5.3 更新报名状态
`POST /api/v1/admin/registrations/{registrationId}/status`

请求体：
```json
{
  "registrationStatus": "VALID",
  "followUpNote": "已电话确认"
}
```

### 13.5.4 导出报名数据
`POST /api/v1/admin/registrations/export`

说明：
1. P0 仅冻结接口能力，不要求立即异步化
2. 数据量小可同步导出
3. 后续可升级为异步任务

---

## 14. 校验规则

## 14.1 课程创建/更新校验
### 草稿保存
1. 允许部分字段为空
2. 至少需要 `className` 或 `templateId` 之一
3. 时间字段不完整时允许存草稿

### 提交审核/发布校验
必须校验：
1. 课程名称
2. 课程类型
3. 上课时间
4. 开课日期
5. 结束日期
6. 总课次
7. 报名截止时间
8. 最低成班人数
9. 最大人数
10. 价格
11. 适合对象或课程简介至少一项
12. 负责人
13. 不成班处理方式

### 业务逻辑校验
1. `signup_deadline` 不能晚于 `start_date`
2. `current_students` 不能大于 `max_students`
3. 不允许在 `IN_PROGRESS`、`ENDED` 状态修改核心排课字段
4. `allow_waitlist=false` 时，不允许提交候补

## 14.2 报名校验
1. 联系方式格式合法
2. 相同课程、相同联系人、相同学员、短时间重复提交需拦截或提示
3. 当前课程未开放报名时，正式报名接口不可用
4. 满员时正式报名不可写入 `ENROLLMENT`
5. 候补仅允许在 `FULL`、`WAITLIST_OPEN` 或配置允许的进行中场景
6. 试听仅允许在 `allow_trial=true` 时提交

---

## 15. 审计、日志与可观测性

## 15.1 审计范围
以下动作必须审计：
1. 创建课程
2. 更新课程
3. 提交审核
4. 审核通过
5. 审核驳回
6. 发布课程
7. 取消课程
8. 更新报名状态
9. 导出报名名单
10. 权限配置变更

### 15.2 应记录内容
1. 操作人 ID 与角色
2. 请求 ID
3. 目标实体 ID
4. 操作前后状态
5. 关键字段变更快照
6. 执行结果
7. 错误码与失败原因

## 15.3 业务日志
建议分三层：
1. 访问日志
2. 应用日志
3. 审计日志

### 15.4 日志字段规范
推荐统一字段：
- `timestamp`
- `level`
- `service`
- `requestId`
- `userId`
- `action`
- `entityType`
- `entityId`
- `status`
- `errorCode`

## 15.5 指标建议
1. 课程创建成功率
2. 提交审核成功率
3. 审核通过率/驳回率
4. 报名提交成功率
5. 候补提交成功率
6. API P95 延迟
7. 5xx 错误率

---

## 16. 错误处理设计

## 16.1 原则
1. 错误码稳定、文案可读
2. 前端依赖错误码，不依赖中文文案判断逻辑
3. 参数错误、权限错误、状态错误、系统错误必须分类
4. 关键失败必须写日志并带 `requestId`

## 16.2 错误码分类
1. `VALIDATION_*` 参数校验错误
2. `AUTH_*` 认证错误
3. `PERMISSION_*` 权限错误
4. `CLASS_*` 课程业务错误
5. `REGISTRATION_*` 报名业务错误
6. `SYSTEM_*` 系统错误

### 16.3 典型错误码
1. `PERMISSION_DENIED`
2. `CLASS_NOT_FOUND`
3. `CLASS_STATUS_INVALID`
4. `CLASS_REVIEW_COMMENT_REQUIRED`
5. `CLASS_PUBLISH_VALIDATION_FAILED`
6. `REGISTRATION_DUPLICATED`
7. `REGISTRATION_NOT_ALLOWED`
8. `WAITLIST_NOT_ALLOWED`
9. `TRIAL_NOT_ALLOWED`
10. `SYSTEM_INTERNAL_ERROR`

## 16.4 前端反馈原则
1. 表单字段错误就近提示
2. 状态错误使用全局提示并刷新数据
3. 权限错误引导用户返回列表或隐藏操作
4. 系统错误提示“请稍后重试”，同时后端记录详情

---

## 17. 非功能需求

## 17.1 性能
1. 看板列表接口 P95 < 300ms
2. 课程详情接口 P95 < 300ms
3. 报名提交接口 P95 < 500ms
4. 后台课程列表接口 P95 < 500ms

## 17.2 可用性
1. 核心接口可用性目标 99.9%
2. 关键写操作具备失败重试与幂等防护思路
3. 后台导出失败不影响主业务链路

## 17.3 安全
1. 后台接口必须鉴权
2. 后台写操作必须做 CSRF/Token 防护
3. 个人信息字段需脱敏展示
4. 导出权限严格限制
5. 审计日志不可随业务数据一并删除

## 17.4 数据保护
1. 联系方式属于敏感信息，日志中默认脱敏
2. 导出文件应设置有效期或权限边界
3. 软删除优先，便于审计追溯

## 17.5 可维护性
1. 统一枚举定义
2. 统一错误码定义
3. 统一 DTO 与领域对象映射规范
4. 所有关键业务规则需有单测

## 17.6 可测试性
1. 权限路径可独立测试
2. 状态机路径可独立测试
3. API 契约可做集成测试
4. 审计产出可做断言

---

## 18. 并行开发与串行依赖

## 18.1 可并行工作
在以下冻结项完成后，可并行：
1. 前端后台课程列表页开发 与 后端课程列表接口开发
2. 前端创建/编辑页开发 与 后端草稿接口开发
3. 前台看板/详情页开发 与 后端公开查询接口开发
4. 报名表单页开发 与 后端报名接口开发
5. QA 用例准备 与 功能开发
6. issue log / progress 文档更新 与 编码工作

## 18.2 必须串行的工作
以下工作必须按顺序：
1. 冻结状态枚举 -> 才能开始前后台状态展示与状态流转开发
2. 冻结字段契约 -> 才能开始表单与 API 联调
3. 冻结权限边界 -> 才能开始后台操作按钮与权限校验开发
4. 完成 Batch 0 评审 -> 才能进入 Batch 1 编码
5. 完成 Batch 1 数据模型 -> 才能稳定进入 Batch 2 审核流与 Batch 3 查询展示开发

## 18.3 推荐任务拆分
### Track A：架构/后端准备
1. 建表方案
2. 枚举定义
3. DTO 契约
4. 状态机校验器
5. 审计中间件

### Track B：前端开发
1. 页面骨架
2. 表单字段映射
3. 状态标签渲染
4. 动作权限控制

### Track C：测试/验收
1. 权限路径清单
2. 状态流转清单
3. 表单校验清单
4. 审计验收清单

---

## 19. 冻结契约清单

Batch 0 结束前必须冻结以下契约，后续变更需走评审：

### 19.1 枚举冻结
1. 课程状态枚举
2. 报名类型枚举
3. 报名状态枚举
4. 课程类型枚举
5. 不成班处理方式枚举

### 19.2 字段冻结
1. 课程列表字段
2. 课程详情字段
3. 课程创建/编辑字段
4. 报名表单字段
5. 候补表单字段
6. 报名管理列表字段

### 19.3 权限冻结
1. 角色定义
2. 操作动作集合
3. 资源归属规则
4. 前端 `actions` 返回方式

### 19.4 状态机冻结
1. 主状态集合
2. 合法流转关系
3. 驳回理由必填规则
4. 发布前完整校验规则

### 19.5 API 冻结
1. 路由命名
2. 请求体字段名
3. 响应体字段名
4. 错误码格式
5. 通用响应包装格式

---

## 20. 设计评审结论

### 20.1 评审结论
当前方案满足 PRD、UI 设计文档与治理文档对 Batch 0 的要求，可作为进入 Batch 1 的后端设计基线。

结论依据：
1. 已覆盖课程、审核、报名、模板、审计五类核心对象
2. 已明确角色权限边界，符合“管理员 / 指定发起人 / 普通用户”职责划分
3. 已定义课程状态机与报名状态，支撑 UI 的状态展示规范
4. 已冻结列表页、详情页、表单页、后台管理页所需核心字段
5. 已明确并行开发前提与串行依赖，符合治理规范
6. 已预留支付、通知、自动状态等后续演进空间，但未提前引入过度复杂度

### 20.2 准入建议
满足以下条件后，Hermes 可批准进入 Batch 1：
1. 本文档评审通过
2. 测试与验收文档补齐
3. issue log 与 progress 文档初始化完成
4. 前后端确认冻结字段与枚举无异议

---

## 21. 开放问题

以下问题需在 Batch 1 开发前确认：

1. 课程管理员是否具备“直接发布”权限，还是必须统一经过审核流程。
2. `REJECTED` 是否作为数据库显式状态保留，还是只写审核记录并回写为 `DRAFT`。
3. 普通用户报名是否要求登录，还是允许匿名留资。
4. 重复报名的判重规则是否以“课程 + 联系方式 + 学员姓名”为唯一组合。
5. 课程封面上传使用何种存储服务，是否需要图片处理。
6. FAQ 字段是否按结构化数组存储，还是先按富文本存储。
7. 负责人是否必须为后台用户，还是允许录入外部老师信息。
8. 导出报名名单是否在 P0 范围内仅保留接口占位，还是 Batch 4 必须交付。
9. 前台是否展示 `IN_PROGRESS` 课程，如果展示，CTA 是否全部关闭。
10. 试听申请是否独立流程处理，还是统一进入报名管理并靠 `registerType=TRIAL` 区分。

---

## 22. 附录：推荐实现顺序

### 22.1 Batch 1 优先实现
1. `classes`、`registrations`、`class_templates` 建表
2. 后台课程列表接口
3. 创建课程草稿接口
4. 编辑草稿接口
5. 后台课程详情接口

### 22.2 Batch 2 优先实现
1. 角色判定与资源级权限校验
2. 提交审核接口
3. 审核通过/驳回接口
4. 发布与前台可见性过滤

### 22.3 Batch 3 优先实现
1. 前台课程看板列表接口
2. 前台课程详情接口
3. 状态标签与 CTA 动作计算

### 22.4 Batch 4 优先实现
1. 报名接口
2. 候补接口
3. 报名管理列表与详情接口
4. 报名状态更新与导出能力

---

## 23. 最终结论

本架构设计采用“单体应用 + 清晰模块边界 + 显式状态机 + 资源级权限 + 审计默认开启”的方案，能以较低复杂度支撑拼课课程系统 P0 范围，并为后续支付、通知、自动化扩展保留足够演进空间。

对于 Batch 0，本设计已完成应冻结的后端契约定义，建议在完成测试与验收文档、issue log、progress 文档后进入正式开发。
