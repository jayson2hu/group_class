# 拼课课程系统 — PRD vs 实现 Gap Analysis

Date: 2026-04-14
Status: Review
Owner: Hermes

---

## 1. 总体判断

当前原型已完成 Batch 1 ~ Batch 5 后端核心闭环（85 passed），前端 UI 已完成前台看板/详情/报名/后台列表/后台详情的重设计。整体覆盖了 PRD 阶段一 MVP 约 60-65% 的功能面，但仍有若干 PRD 明确要求的 P0 能力尚未落地或仅部分落地。

---

## 2. 已完成能力一览

| 领域 | 已落地能力 |
|---|---|
| 课程模型 | GroupClass 全字段建模、DRAFT 创建、更新、详情、列表 |
| 审核流 | submit_review / approve / reject，DRAFT -> PENDING_REVIEW -> OPEN_FOR_ENROLLMENT / REJECTED |
| 权限 | INITIATOR 资源归属限制、CLASS_ADMIN / SUPER_ADMIN 审核门禁、creator_id / reviewer_id 持久化 |
| 前台可见性 | public_only 过滤，6 种公开可见状态，状态标签 / 差额文案 / 剩余名额 / CTA 映射 |
| 详情页内容 | courseSubtitle、适合/不适合人群、课程目标、排课摘要、课时、规则、FAQ |
| 报名 | ENROLLMENT / WAITLIST / TRIAL 三种类型提交，必填校验，课程人数联动 |
| 报名管理 | 后台列表、详情、备注更新、状态管理（VALID / INVALID / CANCELLED） |
| 模板 | 模板存在/启用校验、字段自动回填、复制建课（sourceClassId） |
| 持久化 | InMemory + SQLite 双仓储，schema / index / 约束表达 |
| 前端 | 前台看板、详情、报名表单、后台列表、后台详情、响应式、loading 状态 |

---

## 3. 功能缺失清单（PRD P0 范围内）

### 3.1 后端 API 路由缺失

server.py 当前仅暴露 5 条路由，大量已实现的控制器能力未接入 HTTP 层：

| 缺失路由 | 对应控制器 | PRD 章节 |
|---|---|---|
| `POST /api/v1/admin/classes` | create_class_draft | 7.6 创建课程 |
| `PUT /api/v1/admin/classes/:id` | update_class_draft | 7.6 编辑课程 |
| `POST /api/v1/admin/classes/:id/submit-review` | submit_class_review | 7.7 审核流 |
| `POST /api/v1/admin/classes/:id/approve` | approve_class_review | 7.7 审核流 |
| `POST /api/v1/admin/classes/:id/reject` | reject_class_review | 7.7 审核流 |
| `GET /api/v1/admin/registrations` | list_registrations | 7.9 报名管理 |
| `GET /api/v1/admin/registrations/:id` | get_registration_detail | 7.9 报名管理 |
| `PUT /api/v1/admin/registrations/:id/notes` | update_registration_notes | 7.9 报名管理 |
| `PUT /api/v1/admin/registrations/:id/status` | update_registration_status | 7.9 报名管理 |

### 3.2 后台前端页面缺失

| 缺失页面 | PRD 章节 | 说明 |
|---|---|---|
| 后台创建/编辑课程页 | 7.6 | 前端无创建/编辑表单，无法通过 UI 创建课程 |
| 后台审核操作 UI | 7.7 | 后台列表有 action tag 展示，但无提交审核/通过/驳回的交互按钮与确认流 |
| 后台报名管理页 | 7.9 | 前端无报名列表/详情/备注/状态管理页面 |
| 后台模板管理页 | 7.8 | 前端无模板 CRUD 界面 |

### 3.3 后端能力缺失

| 缺失能力 | PRD 章节 | 说明 |
|---|---|---|
| 模板 CRUD 接口 | 7.8 | 模板仅有读取 Protocol，无创建/更新/删除/列表控制器与仓储写路径 |
| 报名导出 | 7.9 | PRD 要求"导出报名名单"，当前无导出能力 |
| 课程下架/取消 | 7.5 | PRD 列出"下架""取消"操作，当前无对应状态流转 |
| 课程删除 | 7.5 | PRD 列出超级管理员可删除课程，当前无实现 |
| 自动状态计算 | 8.3 | PRD 建议状态切换规则（60% 即将成班、满员等），当前状态完全手动 |
| 候补转正 | 6.3 | PRD 描述"若有空位，运营通知转正"，当前无候补转正流程 |
| 报名"转其他课程" | 7.9 | PRD 列出"转其他课程"操作，当前无实现 |
| 分页参数透传 | 7.5 | server.py 硬编码 page=1, page_size=50，前端无分页控件 |
| 课程封面图 | 7.6 | PRD 要求课程封面字段，模型中未建模 |
| 课程亮点/简介 | 7.6 | PRD 列出 class_highlights / class_notice，模型中未建模 |
| 课程负责人 (owner_id) | 7.5 | PRD 数据结构有 owner_id，模型中未建模 |
| 报名截止自动关闭 | 6.1 | PRD 描述报名截止时间，当前无定时任务或截止判断 |
| 支付状态 (payment_status) | 9.2 | PRD 数据结构有 payment_status，模型中未建模（P1 可延后） |

### 3.4 前台功能缺失

| 缺失功能 | PRD 章节 | 说明 |
|---|---|---|
| 课程看板 FAQ 区域 | 10.1 | PRD 要求看板底部有通用 FAQ 区域，当前未实现 |
| 报名成功页增强 | 7.3 | 当前成功页较简单，PRD 要求"展示当前课程状态与后续通知说明" |
| 候补表单独立页 | 7.4 | 当前候补复用报名表单，PRD 定义了独立候补字段集（含"是否接受其他相近课程推荐"） |
| 课程筛选/搜索 | 10.2 | PRD 建议后台支持状态/创建人/时间/类型筛选，当前无筛选 |
| 分享链接 | 11 | PRD 非功能需求"所有已发布课程应支持分享链接"，当前无分享入口 |

### 3.5 非功能 / 工程缺失

| 缺失项 | 说明 |
|---|---|
| 认证/鉴权中间件 | server.py 无任何认证，后台接口对外完全开放 |
| 前后台路由隔离 | PRD 要求"普通用户不可见后台入口"，当前导航栏同时展示前台/后台 |
| SQLite 未接入 server.py | server.py 使用 InMemoryRepository，SQLite 仓储仅在测试中使用 |
| 错误处理 / 用户友好提示 | 前端 API 错误仅显示"提交失败，请稍后重试"，未解析后端错误详情 |

---

## 4. 优先级建议

### P0-Critical（MVP 闭环必须）

1. 后端路由补齐 — 将已实现的 9 个控制器接入 server.py
2. 后台创建/编辑课程页 — 否则无法通过 UI 创建课程
3. 后台审核操作 UI — 否则审核流无法在前端走通
4. 后台报名管理页 — 否则运营无法查看报名数据
5. 前后台路由隔离 — 至少隐藏后台导航入口或加简单角色判断

### P0-Important（MVP 体验完整）

6. 课程下架/取消状态流转
7. 看板 FAQ 区域
8. 候补表单字段差异化
9. 分页支持
10. 前端错误提示增强

### P1（运营增强，可延后）

11. 模板 CRUD 管理页
12. 报名导出
13. 自动状态计算
14. 候补转正
15. 课程筛选/搜索
16. 课程封面 / 亮点 / 负责人字段补齐
17. 分享链接

### P2（业务闭环，暂不纳入）

18. 支付锁位 / 支付状态
19. 自动通知
20. 报名截止自动关闭
21. 认证/鉴权中间件

---

## 5. 下一步建议

按当前项目节奏，建议优先推进 P0-Critical 的 5 项，形成"后台可创建课程 -> 提交审核 -> 审核通过 -> 前台可见 -> 用户报名 -> 后台查看报名"的完整 UI 闭环。这 5 项完成后，MVP 的核心业务链路才算真正可用。
