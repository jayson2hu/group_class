# 拼课系统专家体验驱动开发计划

Date: 2026-05-10  
Status: Ready for Expert Review and Incremental Execution  
Owner: Jayson  
Depends on: `docs/plans/2026-05-10-role-based-product-experience-research.md`  

---

## 1. 计划目标

本计划用于把“角色化体验研究”转成可执行的产品改进开发任务。

执行原则：

1. 先由对应专家按角色场景体验产品，产出证据化问题。
2. 再把问题合并成最小功能点。
3. 每个小功能点独立开发、独立自测、独立验收、独立提交。
4. 不一次性大改页面，不做没有体验证据支撑的功能。
5. 每完成一个编号，必须更新本文档进度表和完成记录。

---

## 2. 专家组与职责

### E1：家长转化体验专家

对应角色：R1 首次接触家长、R2 候补家长  
关注目标：家长是否能快速判断、安心报名、理解候补和后续流程。

需要重点评审：

- 前台看板是否能在 10 秒内传达关键信息
- 详情页是否支撑报名决策
- 报名/候补表单是否足够轻
- 成功页是否清楚说明后续联系、锁位和候补预期
- 微信移动端是否顺畅

交付物：

- 家长体验问题清单
- 转化阻碍排序
- P0/P1/P2 改进建议

### E2：教务运营效率专家

对应角色：R3 运营老师/教务负责人  
关注目标：是否真的减少微信群统计、Excel 管理和人工跟进成本。

需要重点评审：

- 报名列表是否能快速找出待处理记录
- 候补转正是否清楚、可追踪
- CSV 是否符合运营交付习惯
- 跟进备注是否能支持多人协作
- 后台是否缺少“今日待处理”或运营看板

交付物：

- 运营效率问题清单
- 后台批量处理/筛选/导出改进建议
- 可替代 Excel 程度评分

### E3：课程供给与老师发起专家

对应角色：R4 指定发起人/老师  
关注目标：老师是否能低成本用模板创建课程并提交审核。

需要重点评审：

- 模板是否真的降低创建成本
- 表单字段是否过重
- 草稿保存后下一步是否明确
- 审核状态是否易懂
- 驳回后是否知道怎么修改

交付物：

- 创建课程流程问题清单
- 模板和表单简化建议
- 审核流体验建议

### E4：平台治理与审核专家

对应角色：R5 平台管理员/审核人  
关注目标：课程质量、权限、审核、负责人机制是否可控。

需要重点评审：

- 待审核课程是否容易发现
- 课程完整性是否足以发布
- 审核通过/驳回是否有证据和原因
- 负责人、创建人、模板来源是否能辅助判断
- 是否存在普通用户看到后台或越权风险

交付物：

- 审核治理问题清单
- 发布前完整性校验建议
- 权限/状态/审计改进建议

### E5：业务经营与增长专家

对应角色：R6 业务负责人/校区负责人  
关注目标：系统是否支持判断成班效率、招生瓶颈和运营动作。

需要重点评审：

- 是否能识别“差 1 人成班”的重点课程
- 是否能按负责人/课程类型/模板看效果
- 是否能发现报名停滞、候补多、信息质量差的问题
- 是否能给出下一步运营动作

交付物：

- 经营视角问题清单
- 运营看板和指标建议
- 增长动作建议

### E6：移动端可用性与可访问性专家

对应场景：S1 微信内移动端体验、S4 高负载后台  
关注目标：关键流程在移动端和高数据量下是否可用。

需要重点评审：

- 375px 移动端看板、详情、表单是否易用
- 按钮、输入、Toast、底部 CTA 是否遮挡或误触
- 长列表、分页、筛选是否可用
- 分享链接在 HTTP/HTTPS/微信环境的降级是否清楚

交付物：

- 移动端问题清单
- 交互与响应式布局建议
- 发布前 UI 回归清单

---

## 3. 专家体验阶段计划

| 阶段 | 专家 | 场景 | 输出 | 状态 |
|---|---|---|---|---|
| X1 | E1 家长转化体验专家 | R1/R2 | 家长报名与候补体验报告 | ✅ 已完成 |
| X2 | E2 教务运营效率专家 | R3 | 运营后台效率体验报告 | ✅ 已完成 |
| X3 | E3 课程供给专家 | R4 | 老师建课与模板体验报告 | ✅ 已完成 |
| X4 | E4 平台治理专家 | R5 | 审核治理体验报告 | ✅ 已完成 |
| X5 | E5 业务经营专家 | R6 | 经营指标与看板体验报告 | ✅ 已完成 |
| X6 | E6 移动端专家 | S1-S4 | 移动端与压力体验报告 | ✅ 已完成 |
| X7 | 产品负责人汇总 | 全部报告 | 合并问题池和优先级排序 | ✅ 已完成 |

专家报告统一输出到：

`docs/reviews/2026-05-10-product-experience-review.md`

---

## 4. 候选开发任务池

以下任务来自角色化体验文档中的高概率问题。实际执行前，应先完成 X1-X7 专家体验，按证据调整优先级。

### P0：上线前优先验证/修复

| 编号 | 功能 | 主要角色 | 范围 | 状态 |
|---|---|---|---|---|
| K1 | 前台课程卡片决策信息增强 | E1 | 前端 | ⬜ 待评审确认 |
| K2 | 报名成功页后续预期增强 | E1 | 前端 | ⬜ 待评审确认 |
| K3 | 候补成功预期增强 | E1/E2 | 后端 + 前端 | ⬜ 待评审确认 |
| K4 | 报名列表状态筛选和待跟进视图 | E2 | 后端 + 前端 | ⬜ 待评审确认 |
| K5 | 发布前课程完整性校验 | E4 | 后端 + 前端 | ⬜ 待评审确认 |

### P1：上线后第一轮优化

| 编号 | 功能 | 主要角色 | 范围 | 状态 |
|---|---|---|---|---|
| K6 | 报名详情操作历史 | E2/E4 | 后端 + 前端 | ⬜ 待评审确认 |
| K7 | 创建课程表单分步化 | E3/E6 | 前端 | ⬜ 待评审确认 |
| K8 | 驳回原因结构化 | E3/E4 | 后端 + 前端 | ⬜ 待评审确认 |
| K9 | 运营看板 MVP | E2/E5 | 后端 + 前端 | ⬜ 待评审确认 |
| K10 | CSV 导出字段增强 | E2/E5 | 后端 | ⬜ 待评审确认 |

### P2：增强能力

| 编号 | 功能 | 主要角色 | 范围 | 状态 |
|---|---|---|---|---|
| K11 | 相近课程自动推荐 | E1/E5 | 后端 + 前端 | ⬜ 待评审确认 |
| K12 | 报名截止自动关闭 | E2/E4 | 后端 | ⬜ 待评审确认 |
| K13 | 自动通知接口预留 | E2/E5 | 后端 | ⬜ 待评审确认 |
| K14 | 经营数据分析看板增强 | E5 | 后端 + 前端 | ⬜ 待评审确认 |

---

## 5. 首批建议开发小功能

如果专家体验后没有推翻假设，建议第一轮只做 K1-K5。它们直接影响家长转化、运营效率和发布质量。

### K1：前台课程卡片决策信息增强

**专家来源**  
E1 家长转化体验专家、E6 移动端专家

**问题假设**  
家长在看板上需要更快判断课程是否适合孩子。当前卡片已有价格、人数、时间、进度，但“适合年级/基础/亮点”不够显性。

**目标**  
让家长在 10 秒内知道：

- 适合谁
- 还差几人成班/是否满员
- 价格和时间
- 课程亮点

**范围**

- 前端：`apps/group_class_frontend/js/app.js`
- 样式：`apps/group_class_frontend/css/styles.css`
- 后端：通常不需要，优先复用 `targetAudience`、`highlights`、`progressText`

**最小实现**

- 课程卡片增加 1-2 个信息标签：
  - `targetAudience` 摘要
  - `highlights` 第一行摘要
- 不新增复杂字段。
- 移动端保证不挤压 CTA。

**验收标准**

1. 前台看板卡片显示适合对象摘要
2. 有 `highlights` 时展示亮点摘要，无值时不展示空占位
3. 375px 宽度下文字不溢出按钮
4. `node --check apps/group_class_frontend/js/app.js` 通过

**提交要求**

Commit message: `feat: improve public class cards`

---

### K2：报名成功页后续预期增强

**专家来源**  
E1 家长转化体验专家

**问题假设**  
报名成功后，家长仍可能不知道“是否锁位、是否收费、多久联系、谁联系”，会回到微信群追问。

**目标**  
成功页明确告诉用户：

- 当前只是报名/候补/试听申请
- 预计联系时间
- 是否需要等待人工确认
- 可返回课程详情或复制链接

**范围**

- 前端：`apps/group_class_frontend/js/app.js`

**最小实现**

- 成功页新增“后续流程”三步说明：
  1. 已收到申请
  2. 运营/老师确认
  3. 确认后通知安排
- ENROLLMENT、WAITLIST、TRIAL 使用不同文案。

**验收标准**

1. 正式报名成功页显示“等待人工确认”说明
2. 候补成功页显示“有空位后通知”说明
3. 试听成功页显示“老师/运营联系确认试听”说明
4. 页面无后端详情获取失败崩溃
5. `node --check apps/group_class_frontend/js/app.js` 通过

**提交要求**

Commit message: `feat: clarify registration success next steps`

---

### K3：候补成功预期增强

**专家来源**  
E1 家长转化体验专家、E2 教务运营效率专家

**问题假设**  
候补用户需要知道自己进入了候补队列，但当前没有明确队列位置或候补人数反馈。

**目标**  
候补提交后给用户明确预期，减少群内追问。

**范围**

- 后端：`apps/group_class_backend/registrations/controller.py`
- 前端：`apps/group_class_frontend/js/app.js`
- 测试：`tests/group_class_backend/registrations/`、`tests/test_api/`

**最小实现**

- WAITLIST 提交成功响应增加：
  - `waitlistCount`
  - `waitlistPosition`（最小可用规则：当前候补数）
- 成功页展示“当前候补人数/候补位置”。

**验收标准**

1. WAITLIST 提交后响应包含 `waitlistCount`
2. WAITLIST 提交后响应包含 `waitlistPosition`
3. 成功页展示候补位置或候补人数
4. ENROLLMENT/TRIAL 不受影响
5. `uv run pytest tests/ -q` 通过
6. `node --check apps/group_class_frontend/js/app.js` 通过

**提交要求**

Commit message: `feat: show waitlist position after submit`

---

### K4：报名列表状态筛选和待跟进视图

**专家来源**  
E2 教务运营效率专家

**问题假设**  
运营在报名记录较多时，需要快速找到候补、待确认、有效、已取消等记录。当前报名列表只有分页，没有筛选。

**目标**  
让运营能快速定位待处理报名。

**范围**

- 后端：`apps/group_class_backend/registrations/controller.py`
- 路由：`apps/group_class_backend/routers/registrations.py`
- 前端：`apps/group_class_frontend/js/api.js`、`apps/group_class_frontend/js/app.js`
- 样式：`apps/group_class_frontend/css/styles.css`
- 测试：`tests/test_api/test_registrations_api.py`

**最小实现**

- `GET /api/v1/admin/registrations` 支持：
  - `registrationStatus`
  - `registerType`
  - `keyword`（匹配家长/学生/课程）
- 前端报名列表新增筛选栏：
  - 报名类型
  - 报名状态
  - 关键词
- 筛选条件写入 hash query。

**验收标准**

1. 按 `registerType=WAITLIST` 只返回候补
2. 按 `registrationStatus=VALID` 只返回有效记录
3. keyword 可匹配课程名或家长名
4. 前端筛选后列表刷新且分页回到第一页
5. `uv run pytest tests/ -q` 通过
6. `node --check api.js/app.js` 通过

**提交要求**

Commit message: `feat: filter admin registrations`

---

### K5：发布前课程完整性校验

**专家来源**  
E4 平台治理与审核专家

**问题假设**  
如果课程缺少关键决策信息仍可发布，前台会显得不可信，家长仍会回到群里问问题。

**目标**  
审核/发布前阻止明显不完整的课程进入前台。

**范围**

- 后端：`apps/group_class_backend/classes/controller.py`
- 前端：`apps/group_class_frontend/js/app.js`
- 测试：`tests/group_class_backend/classes/`、`tests/test_api/test_classes_api.py`

**最小校验字段**

提交审核或审核通过前至少要求：

- `className`
- `priceAmount`
- `minStudents`
- `maxStudents`
- `scheduleSummary`
- `targetAudience`
- `courseGoal`
- `groupRule`

**实现建议**

- 优先在 `submit_class_review` 做校验，避免低质量草稿进入审核队列。
- 前端在详情页/提交审核失败时展示中文错误。

**验收标准**

1. 缺少关键字段的草稿提交审核返回 400
2. 错误 details 指明缺失字段
3. 完整课程可正常提交审核
4. 前端 toast 显示可理解错误
5. `uv run pytest tests/ -q` 通过

**提交要求**

Commit message: `feat: validate class readiness before review`

---

## 6. 专家体验与开发执行流程

每个任务必须按以下流程执行。

### Step 1：专家体验

使用 `docs/plans/2026-05-10-role-based-product-experience-research.md` 中的角色场景执行体验。

输出到：

`docs/reviews/2026-05-10-product-experience-review.md`

### Step 2：产品归纳

把专家意见归并为问题池：

| 问题 ID | 来源专家 | 角色场景 | 证据 | 影响 | 建议优先级 |
|---|---|---|---|---|---|

### Step 3：选择一个最小功能

只选择一个编号进入开发，例如 K1。

禁止：

- 同时做多个 K 编号
- 顺手重构无关代码
- 没有验收标准就开发

### Step 4：开发

按任务范围改动文件。

### Step 5：自测

根据任务类型至少执行：

```bash
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js
uv run pytest tests/ -q
```

如果只改前端，仍建议跑全量 pytest，保持回归口径一致。

### Step 6：更新文档

在本文档对应任务下补充：

```markdown
**完成记录（YYYY-MM-DD）**

- 改动：
- 自测：
- commit:
```

### Step 7：提交

每个 K 编号单独提交。

---

## 7. 进度表

| 编号 | 功能 | 状态 | 自测 | Commit |
|---|---|---|---|---|
| X1 | 家长报名/候补体验报告 | ✅ 已完成 | 文档 review | - |
| X2 | 运营后台体验报告 | ✅ 已完成 | 文档 review | - |
| X3 | 老师建课体验报告 | ✅ 已完成 | 文档 review | - |
| X4 | 平台审核体验报告 | ✅ 已完成 | 文档 review | - |
| X5 | 业务经营体验报告 | ✅ 已完成 | 文档 review | - |
| X6 | 移动端体验报告 | ✅ 已完成 | 文档 review | - |
| X7 | 问题池合并和优先级排序 | ✅ 已完成 | 文档 review | - |
| K1 | 前台课程卡片决策信息增强 | ✅ 已完成 | `node --check app.js`; `node --check api.js`; `uv run pytest tests/ -q` 149 passed | `feat: improve public class cards` |
| K2 | 报名成功页后续预期增强 | ✅ 已确认 | - | - |
| K3 | 候补成功预期增强 | ✅ 已确认 | - | - |
| K4 | 报名列表状态筛选和待跟进视图 | ✅ 已确认 | - | - |
| K5 | 发布前课程完整性校验 | ✅ 已确认 | - | - |

---

## 7.1 完成记录

### K1 完成记录（2026-05-13）

- 前台课程卡片新增“适合”和“亮点”决策标签，分别复用 `targetAudience` 与 `highlights` 第一行摘要。
- 无 `targetAudience` 或 `highlights` 时不展示空标签，避免空占位。
- mock 课程补充 `highlights`，便于本地 mock 模式验证前台效果。
- 移动端样式复用卡片单列布局，避免决策标签挤压 CTA。
- 自测：
  - `node --check apps/group_class_frontend/js/app.js`
  - `node --check apps/group_class_frontend/js/api.js`
  - `/Users/fayun/.local/bin/uv run pytest tests/ -q`（149 passed）
- Commit：`feat: improve public class cards`

## 8. 验收口径

### 专家体验验收

专家体验阶段完成必须满足：

- 每个专家至少输出 5 条观察
- 每条 P0/P1 建议必须有页面/流程证据
- 至少覆盖 1 个移动端场景
- 至少覆盖 1 个后台高负载场景

### 开发任务验收

开发任务完成必须满足：

- 任务验收标准全部通过
- 自动化测试通过
- 文档完成记录已更新
- 单功能 commit 已完成
- 不引入无关改动

---

## 9. 不在本轮做的事

以下内容除非专家体验明确判定为 P0，否则不进入首批 K1-K5：

- 支付锁位
- 真实 JWT 鉴权
- 短信/微信通知真实接入
- CRM 自动跟进
- 智能分班推荐
- 完整 BI 看板
- 大规模 UI 重构

---

## 10. 下一步建议

下一步先执行 X1-X7，而不是直接开工 K1-K5。

推荐第一轮专家体验顺序：

1. E1 家长转化体验专家
2. E2 教务运营效率专家
3. E3 课程供给与老师发起专家
4. E4 平台治理与审核专家
5. E6 移动端可用性专家
6. E5 业务经营专家
7. 产品负责人合并问题池

合并后，如没有更高优先级问题，按 K1 → K2 → K3 → K4 → K5 逐项开发、验收、提交。
