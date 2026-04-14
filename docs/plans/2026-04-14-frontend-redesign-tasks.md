# 前端 UI 重设计任务书

Date: 2026-04-14
Status: Ready for Codex Execution
Owner: Hermes

---

## Codex 开发进度与验收记录（2026-04-14）

### 1) 任务完成状态（按 F1 → F10）

| 任务 | 状态 | 实施结果 |
|---|---|---|
| F1 | 已完成 | `app.js` 新增 `showToast(message, type)`，挂载 `window.showToast`；`styles.css` 新增 `toast-container/toast-enter/toast-exit`。全部 `window.alert` 已替换为 toast。 |
| F10 | 已完成 | 新增 `emptyStateHtml`、`errorStateHtml`；前台列表、前台详情、后台课程/报名页面统一空/错状态。 |
| F2 | 已完成 | 前台详情页重构为 hero + 适合/目标 + 规则说明 + FAQ + 底部 CTA，空字段统一“暂未配置”。 |
| F3 | 已完成 | 报名表单重构为三分组，补齐必填标识、placeholder、WAITLIST 选填逻辑、提交 loading 态。 |
| F4 | 已完成 | 报名成功页重构为绿色勾图标 + 信息卡片 + 后续说明 + 双按钮操作栏。 |
| F9 | 已完成 | 前台看板底部新增 5 条通用 FAQ 区域（浅蓝背景 + 网格卡片）。 |
| F5 | 已完成 | 后台创建/编辑表单重构为三分组（基础信息/拼课规则/展示文案），保存按钮 loading + toast。 |
| F6 | 已完成 | 后台课程详情重构为指标卡片/facts/侧栏规则与 FAQ/审核操作区，审核反馈统一 toast。 |
| F7 | 已完成 | 报名管理列表重构为卡片布局，新增按类型统计 pill，类型 chip 颜色区分。 |
| F8 | 已完成 | 报名详情重构为信息区 + 备注区 + 状态区，下拉中文标签，提交反馈统一 toast。 |

### 2) 自测执行结果

已执行：

- `node --check apps/group_class_frontend/js/app.js`：通过
- `node --check apps/group_class_frontend/js/api.js`：通过
- `Invoke-WebRequest http://127.0.0.1:5173/`：HTTP 200
- `Invoke-WebRequest http://127.0.0.1:18000/api/v1/public/classes`：HTTP 200
- `D:/software/anacond/python.exe -m pytest tests/group_class_backend -q`：`91 passed`

实现一致性检查（关键点）：

- Toast 能力与样式存在：`showToast/window.showToast`、`.toast-container/.toast-enter/.toast-exit`
- 空/错状态能力与样式存在：`emptyStateHtml/errorStateHtml`、`.unified-state/.state-icon`
- 无 `window.alert` 残留（代码搜索为空）
- F2/F3/F4/F5/F6/F7/F8/F9 关键结构类名均已落地并在 CSS 有对应样式

### 3) 验收结论

- 结论：`Conditional-Go`
- 代码层面：F1-F10 全部完成并按顺序落地。
- 自测层面：前端语法检查、服务可用性、关键能力点检查均通过。
- 剩余风险：当前为非浏览器自动化验收，建议按文档“全量验收 1-12”再做一次人工走查（特别是 640px 下布局与交互手感）。

---

## 设计原则

- 视觉语言：延续现有设计系统（CSS 变量、圆角卡片、渐变 hero、metric-tile），不引入新框架
- 信息层次：每个页面遵循 hero → 核心指标 → 详细内容 → 操作区 的四层结构
- 交互反馈：所有写操作增加 toast 提示替代 alert，操作按钮增加 loading 态
- 移动端：所有新增布局必须在 900px / 640px 断点下可用
- 文件范围：仅修改 `apps/group_class_frontend/` 下的 `css/styles.css`、`js/app.js`、`index.html`

---

## 任务总览

| 编号 | 任务名称 | 改动文件 | 前置 |
|---|---|---|---|
| F1 | Toast 通知组件 | styles.css, app.js | 无 |
| F2 | 前台课程详情页完整重设计 | app.js, styles.css | 无 |
| F3 | 报名表单体验增强 | app.js, styles.css | 无 |
| F4 | 报名成功页重设计 | app.js, styles.css | 无 |
| F5 | 后台课程创建/编辑表单重设计 | app.js, styles.css | F1 |
| F6 | 后台课程详情页完整重设计 | app.js, styles.css | F1 |
| F7 | 后台报名管理列表页重设计 | app.js, styles.css | F1 |
| F8 | 后台报名详情页重设计 | app.js, styles.css | F1 |
| F9 | 前台看板 FAQ 区域 | app.js, styles.css | 无 |
| F10 | 空状态与错误状态统一 | app.js, styles.css | 无 |

---

## F1：Toast 通知组件

修改文件：`css/styles.css`, `js/app.js`

### 功能描述

替代所有 `window.alert()` 调用，新增轻量 toast 通知，支持 success / error / info 三种类型，3 秒后自动消失。

### 接口契约

在 `app.js` 顶部新增：
```javascript
function showToast(message, type = "info") {
  // type: "success" | "error" | "info"
  // 创建 toast DOM 元素，追加到 body
  // 3 秒后自动移除，支持手动点击关闭
}
```

### CSS 新增

```
.toast-container — 固定在视口右上角，z-index: 1000
.toast — 圆角卡片，左侧 4px 色条（success 绿/error 红/info 蓝）
.toast-enter — 从右侧滑入动画
.toast-exit — 淡出动画
```

### 自测要求

- 在浏览器控制台调用 `showToast("测试成功", "success")`
- 确认右上角出现绿色 toast，3 秒后自动消失
- 调用 `showToast("出错了", "error")` 确认红色 toast
- 快速连续调用 3 次，确认 toast 堆叠不重叠

### 验收标准

1. toast 从右侧滑入，3 秒后淡出消失
2. success 左侧色条为 `var(--ok)`，error 为 `var(--danger)`，info 为 `var(--primary)`
3. 多个 toast 垂直堆叠，间距 8px
4. 移动端 toast 宽度自适应（max-width: 90vw）
5. 所有原有 `window.alert()` 调用替换为 `showToast()`

---

## F2：前台课程详情页完整重设计

修改文件：`js/app.js`, `css/styles.css`

### 问题

当前 `renderPublicDetail` 只渲染了 hero + 侧栏决策信息，缺少适合对象、课程目标、规则说明、FAQ 等内容区，与 PRD 7.2 要求差距大。

### 目标页面结构

```
┌─────────────────────────────────────────────┐
│ detail-hero（现有，保留）                      │
│  左：课程名/副标题/状态/进度/指标卡片           │
│  右：报名决策侧栏（时间/周期/门槛/CTA）        │
└─────────────────────────────────────────────┘
┌──────────────────────┬──────────────────────┐
│ 适合对象 / 不适合对象  │ 课程目标              │
│ （左卡片）            │ （右卡片）             │
└──────────────────────┴──────────────────────┘
┌─────────────────────────────────────────────┐
│ 规则说明（全宽卡片）                           │
│  四列网格：成班规则 | 缺课规则 | 候补规则 | 不成班 │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ FAQ 摘要（全宽卡片，浅蓝背景）                  │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ 底部 CTA 栏：立即报名 / 加入候补 / 返回看板     │
└─────────────────────────────────────────────┘
```

### 实现要点

- 修改 `renderPublicDetail(classId)` 函数
- hero 区保留现有结构，补充 `detail-metrics` 三个指标卡片（剩余名额/价格/人数）
- hero 下方新增 `detail-content-grid`（两列）：左卡片展示适合/不适合对象，右卡片展示课程目标
- 新增 `detail-rules-panel`（全宽）：四列网格展示 groupRule / absenceRule / waitlistRule / failureRule
- 新增 `detail-faq-panel`（全宽，浅蓝背景）：展示 faqSummary
- 底部新增固定 CTA 栏 `detail-bottom-cta`

### CSS 新增

```
.detail-rules-panel — 全宽 panel，内部 4 列 grid
.detail-rule-card — 每个规则卡片，图标 + 标题 + 内容
.detail-faq-panel — 浅蓝背景 panel（var(--primary-soft)）
.detail-bottom-cta — 底部粘性 CTA 栏，白色背景 + 上边框阴影
```

### 自测要求

- 打开前台详情页 `#/public/classes/{classId}`
- 确认 hero 区、适合对象、课程目标、规则说明、FAQ、底部 CTA 全部渲染
- 缩小浏览器到 640px 宽度，确认所有区域变为单列

### 验收标准

1. 详情页包含 hero、适合/不适合对象、课程目标、规则说明、FAQ、底部 CTA 共 6 个区域
2. 规则说明区域展示 4 条规则，每条有标题和内容
3. FAQ 区域有浅蓝背景区分
4. 底部 CTA 栏包含报名/候补按钮和返回看板链接
5. 字段为空时显示"暂未配置"占位文案
6. 900px 以下规则网格变为 2 列，640px 以下变为 1 列

---

## F3：报名表单体验增强

修改文件：`js/app.js`, `css/styles.css`

### 问题

当前 `enrollmentFormHtml` 表单过于简陋：缺少分组标题、流程说明侧栏、必填标识、占位提示。与之前重设计版本（progress 记录 #97）相比有退化。

### 目标页面结构

```
┌─────────────────────────────────────────────┐
│ enrollment-hero                              │
│  左：表单标题 + 说明文案                       │
│  右：提交流程说明侧栏                          │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ 表单区域                                      │
│  ┌─ 家长信息 ─────────────────────────────┐  │
│  │ 家长姓名 *  │  联系方式（手机号）*        │  │
│  └────────────────────────────────────────┘  │
│  ┌─ 学员信息 ─────────────────────────────┐  │
│  │ 学员姓名 *  │  学员年级 *               │  │
│  │ 英语基础 *（全宽）                       │  │
│  └────────────────────────────────────────┘  │
│  ┌─ 补充说明 ─────────────────────────────┐  │
│  │ 备注（全宽 textarea）                    │  │
│  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ form-submit-bar：确认提交 + 返回详情           │
└─────────────────────────────────────────────┘
```

### 实现要点

- 重写 `enrollmentFormHtml(classId, registerType)` 函数
- 恢复 `enrollment-hero` 双列布局（左说明 + 右流程侧栏）
- 表单分三个 `form-section`：家长信息、学员信息、补充说明
- 每个 section 有 `form-section-head`（h3 标题 + muted 说明）
- 必填字段加 `<span class="required-mark">*</span>`
- input 加 `placeholder` 提示
- 候补表单（WAITLIST）：学员姓名非必填，英语基础非必填
- 提交按钮增加 loading 态：提交时 `disabled` + 文案变为"提交中..."

### 自测要求

- 打开 `#/public/enroll/{classId}?type=ENROLLMENT`
- 确认三个分组标题可见：家长信息、学员信息、补充说明
- 确认必填字段有红色 * 标识
- 不填手机号直接提交，确认错误提示出现
- 打开 `?type=WAITLIST`，确认学员姓名和英语基础变为非必填

### 验收标准

1. 表单分三组，每组有标题和说明文案
2. hero 区右侧有流程说明侧栏
3. 必填字段有红色 * 标识和 placeholder
4. 手机号格式错误时表单底部显示红色错误提示
5. 提交过程中按钮显示"提交中..."且不可重复点击
6. WAITLIST 模式下学员姓名和英语基础为选填

---

## F4：报名成功页重设计

修改文件：`js/app.js`, `css/styles.css`

### 问题

当前成功页只有一行文字和返回按钮，缺少课程状态、后续说明、视觉反馈。

### 目标页面结构

```
┌─────────────────────────────────────────────┐
│ success-hero（居中布局）                       │
│  ✓ 大号成功图标（CSS 绘制的圆形勾）            │
│  "报名提交成功"                               │
│  报名编号：reg-xxx                            │
└─────────────────────────────────────────────┘
┌──────────────────────┬──────────────────────┐
│ 报名信息卡片          │ 后续说明卡片           │
│ 报名类型 / 状态       │ nextStepText          │
│ 课程当前状态          │ 温馨提示文案            │
└──────────────────────┴──────────────────────┘
┌─────────────────────────────────────────────┐
│ 操作栏：返回看板 / 查看课程详情                 │
└─────────────────────────────────────────────┘
```

### 实现要点

- 修改报名提交成功后的渲染逻辑（当前在 `bindEnrollmentSubmit` 的 try 块中）
- 新增 `renderEnrollmentSuccess(result, classId)` 函数
- 成功图标用 CSS 绘制：绿色圆形背景 + 白色勾（伪元素）
- 报名信息卡片展示 registrationId、registerType（中文）、registrationStatus
- 后续说明卡片展示 nextStepText + 固定温馨提示

### CSS 新增

```
.success-hero — 居中布局，padding 大
.success-icon — 64px 绿色圆形，白色勾动画
.success-grid — 两列卡片网格
.success-card — 与 summary-pill 类似的卡片样式
```

### 自测要求

- 完成一次报名提交
- 确认成功页显示绿色勾图标、报名编号、报名类型、后续说明
- 确认"返回看板"和"查看课程详情"按钮可点击

### 验收标准

1. 成功页有绿色勾图标（CSS 绘制，非图片）
2. 显示报名编号、报名类型（中文）、报名状态
3. 显示 nextStepText 后续说明
4. 有"返回看板"和"查看课程详情"两个操作按钮
5. 640px 以下两列卡片变为单列

---

## F5：后台课程创建/编辑表单重设计

修改文件：`js/app.js`, `css/styles.css`

### 问题

当前 `adminClassFormHtml` 把 18 个字段全部堆在一个 form-section 里，没有分组，textarea 和 input 混排，视觉层次混乱。

### 目标页面结构

```
┌─────────────────────────────────────────────┐
│ admin-hero：创建新课程 / 编辑课程              │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ form-section：基础信息                        │
│  课程名称 * │ 课程类型 *                      │
│  课程副标题  │ 课程价格                        │
│  订金金额    │                                │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ form-section：拼课规则                        │
│  最少人数 │ 最多人数                           │
│  课时数   │ 上课安排                           │
│  开始日期 │ 结束日期                           │
│  报名截止（全宽）                              │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ form-section：展示文案                        │
│  适合对象（全宽 textarea）                     │
│  不适合对象（全宽 textarea）                   │
│  课程目标（全宽 textarea）                     │
│  拼班规则 │ 缺课规则                           │
│  候补规则 │ 不成班处理                          │
│  FAQ 摘要（全宽 textarea）                     │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ form-submit-bar：保存草稿 + 返回列表           │
└─────────────────────────────────────────────┘
```

### 实现要点

- 重写 `adminClassFormHtml(detail, isEdit)` 函数
- 拆为 3 个 `form-section`，每个有 `form-section-head`（h3 + 说明）
- 基础信息组：className（必填）、classType（下拉，必填）、courseSubtitle、priceAmount、depositAmount
- 拼课规则组：minStudents、maxStudents、sessionCount、scheduleSummary、startDate、endDate、signupDeadline
- 展示文案组：targetAudience、unsuitableAudience、courseGoal、groupRule、absenceRule、waitlistRule、failureRule、faqSummary
- 所有 textarea 设置 `min-height: 80px`
- 规则类 textarea 两列排列（groupRule | absenceRule，waitlistRule | failureRule）
- 编辑模式下 version 作为 hidden input
- 提交按钮增加 loading 态 + toast 反馈（依赖 F1）

### 自测要求

- 打开 `#/admin/classes/new`，确认三个分组标题可见
- 填写必填字段，点击保存，确认 toast 提示"保存成功"
- 打开 `#/admin/classes/{id}/edit`，确认字段回填正确
- 修改课程名称，保存，确认详情页名称更新

### 验收标准

1. 表单分三组：基础信息、拼课规则、展示文案
2. 每组有标题和灰色说明文案
3. 必填字段有红色 * 标识
4. textarea 字段有合理的最小高度
5. 规则类 textarea 两列排列
6. 保存成功后显示 toast 并跳转到详情页
7. 编辑模式下所有字段正确回填

---

## F6：后台课程详情页完整重设计

修改文件：`js/app.js`, `css/styles.css`

### 问题

当前 `renderAdminClassDetail` 只展示了课程名、状态、少量 facts 和审核按钮，缺少指标卡片、完整规则展示、适配/目标信息。

### 目标页面结构

```
┌─────────────────────────────────────────────┐
│ admin-detail-hero                            │
│  左：课程名/副标题/状态标签/进度文案            │
│  右：课程 ID pill + 动作 tags pill             │
└─────────────────────────────────────────────┘
┌──────────────────────────┬──────────────────┐
│ 运营摘要（左主区）         │ 适配与目标（右侧栏）│
│  4 个 metric-tile：       │  适合对象           │
│  剩余名额/人数/价格/课时   │  不适合对象         │
│  facts 网格：             │  课程目标           │
│  类型/时间/周期/截止/规则  │                    │
├──────────────────────────┤  规则与 FAQ         │
│                          │  拼班/候补/缺课/不成班│
│                          │  FAQ 摘要           │
│                          ├──────────────────┤
│                          │ 操作区              │
│                          │ 审核按钮 + 编辑 + 返回│
└──────────────────────────┴──────────────────┘
```

### 实现要点

- 重写 `renderAdminClassDetail(classId)` 函数
- hero 区恢复双列布局：左侧课程信息 + 右侧 summary pills
- 主内容区用 `admin-detail-grid`（左 1.4fr + 右 0.9fr）
- 左主区：4 个 metric-tile + admin-detail-facts 网格（2 列）
- 右侧栏：两个 `admin-side-card`（适配与目标 + 规则与 FAQ）
- 审核按钮放在右侧栏底部操作区
- 审核操作成功后用 toast 提示（依赖 F1）

### 自测要求

- 打开 `#/admin/classes/{classId}`
- 确认 hero 区、指标卡片、facts 网格、适配信息、规则、FAQ、操作按钮全部渲染
- 点击"提交审核"确认 toast 提示 + 页面刷新

### 验收标准

1. 详情页包含 hero、4 个指标卡片、facts 网格、适配与目标、规则与 FAQ、操作区
2. 指标卡片展示剩余名额、当前人数、课程价格、课时数
3. facts 网格展示课程类型、上课时间、开课周期、报名截止、成班规则、最近更新
4. 右侧栏展示适合/不适合对象、课程目标、5 条规则、FAQ 摘要
5. 审核按钮根据状态动态显示（DRAFT→提交审核，PENDING_REVIEW→通过/驳回）
6. 操作成功后 toast 提示而非 alert
7. 900px 以下变为单列布局

---

## F7：后台报名管理列表页重设计

修改文件：`js/app.js`, `css/styles.css`

### 问题

当前 `renderAdminRegistrations` 表格有 10 列，信息密度过高，窄屏下严重溢出。报名类型和状态用纯文本展示，缺少视觉区分。

### 目标页面结构

```
┌─────────────────────────────────────────────┐
│ admin-hero：报名管理                          │
│  左：标题 + 说明                              │
│  右：报名总数 pill + 按类型统计 pills           │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ 报名卡片列表（替代纯表格）                      │
│  ┌─────────────────────────────────────────┐│
│  │ 报名卡片                                 ││
│  │  头部：学员姓名 + 报名类型 chip + 状态 chip ││
│  │  信息行：家长 | 联系方式 | 年级 | 课程名    ││
│  │  底部：提交时间 + 查看按钮                  ││
│  └─────────────────────────────────────────┘│
│  ... 更多卡片                                 │
└─────────────────────────────────────────────┘
```

### 实现要点

- 重写 `renderAdminRegistrations()` 函数
- hero 区增加按类型统计：遍历 items 统计 ENROLLMENT / WAITLIST / TRIAL 数量，各显示一个 summary-pill
- 主内容区改为卡片列表（而非表格），每条报名一个 `registration-card`
- 卡片头部：学员姓名（大字）+ 报名类型 chip + 状态 chip
- 卡片信息行：用 `dl` 展示家长姓名、联系方式、学员年级、课程名称
- 卡片底部：提交时间 + "查看详情"按钮
- 报名类型 chip 颜色：ENROLLMENT → primary，WAITLIST → warn，TRIAL → ok
- 卡片列表用 grid 布局，`grid-template-columns: repeat(auto-fill, minmax(360px, 1fr))`

### CSS 新增

```
.registration-card — panel 基础 + flex column
.registration-card-head — flex，学员名 + chips
.registration-card-info — dl 网格，2 列
.registration-card-footer — flex，时间 + 按钮
.chip.ENROLLMENT — primary 色
.chip.WAITLIST — warn 色
.chip.TRIAL — ok 色
```

### 自测要求

- 先通过前台提交 2-3 条不同类型的报名
- 打开 `#/admin/registrations`
- 确认卡片列表渲染，每张卡片信息完整
- 确认报名类型和状态有不同颜色 chip
- 缩小到 640px，确认卡片变为单列

### 验收标准

1. hero 区显示报名总数和按类型统计
2. 每条报名以卡片形式展示，非表格行
3. 卡片包含学员姓名、报名类型 chip、状态 chip、家长信息、联系方式、课程名、提交时间
4. 报名类型 chip 有颜色区分（报名蓝/候补橙/试听绿）
5. 无报名时显示空状态卡片
6. 640px 以下卡片单列排列

---

## F8：后台报名详情页重设计

修改文件：`js/app.js`, `css/styles.css`

### 问题

当前 `renderAdminRegistrationDetail` 左侧 facts 和右侧表单布局合理，但缺少视觉层次，表单区域没有分组，状态下拉选项缺少中文标签。

### 目标页面结构

```
┌─────────────────────────────────────────────┐
│ admin-detail-hero                            │
│  报名详情 + 报名编号 + 课程名 + 类型 chip      │
└─────────────────────────────────────────────┘
┌──────────────────────────┬──────────────────┐
│ 报名信息（左主区）         │ 操作面板（右侧栏）  │
│  信息卡片：               │                    │
│  家长姓名/联系方式         │ 跟进备注 section    │
│  学员姓名/年级/英语基础    │  textarea + 保存    │
│  备注                    │                    │
│  提交时间/更新时间         │ 状态管理 section    │
│                          │  当前状态 chip       │
│                          │  下拉 + 更新按钮     │
│                          │                    │
│                          │ 返回报名列表         │
└──────────────────────────┴──────────────────┘
```

### 实现要点

- 重写 `renderAdminRegistrationDetail(registrationId)` 函数
- hero 区增加报名类型 chip（复用 F7 的颜色方案）
- 左主区用 `admin-detail-facts` 展示所有报名字段，2 列网格
- 右侧栏分两个 `admin-side-card`：
  - 跟进备注：followUpNote textarea + notes textarea + 保存按钮
  - 状态管理：当前状态 chip 展示 + 下拉选择 + 更新按钮
- 状态下拉选项增加中文标签：`VALID → 有效`、`INVALID → 无效`、`CANCELLED → 已取消`
- 保存备注和更新状态成功后用 toast 提示（依赖 F1）

### 自测要求

- 从报名列表点击"查看详情"进入
- 确认左侧信息完整，右侧两个操作区域可见
- 输入跟进备注，点击保存，确认 toast 提示"备注已保存"
- 选择状态为"有效"，点击更新，确认 toast 提示 + 状态 chip 变化

### 验收标准

1. hero 区显示报名编号、课程名、报名类型 chip
2. 左侧信息区展示所有报名字段（家长、学员、联系方式、年级、英语基础、备注、时间）
3. 右侧跟进备注区有两个 textarea 和保存按钮
4. 右侧状态管理区显示当前状态 chip + 下拉 + 更新按钮
5. 状态下拉选项有中文标签
6. 操作成功后 toast 提示而非 alert
7. 900px 以下变为单列布局

---

## F9：前台看板 FAQ 区域

修改文件：`js/app.js`, `css/styles.css`

### 问题

PRD 10.1 要求看板底部有通用 FAQ 区域，当前完全缺失。

### 实现要点

- 修改 `renderPublicList()`，在课程卡片网格后追加 FAQ section
- FAQ 硬编码 5 条（与 PRD 10.1 一致）：
  1. 什么情况下成班？→ 达到最低成班人数即成班，具体人数见各课程详情。
  2. 不成班怎么办？→ 运营会统一通知转班或退款安排。
  3. 可以试听吗？→ 部分课程支持试听，详见课程详情页。
  4. 缺课怎么办？→ 各课程有不同缺课规则，报名前请查看详情。
  5. 是否支持换班？→ 部分课程支持调班，具体请咨询运营。
- 浅蓝背景 panel，内部 3 列网格，每条 FAQ 白色卡片

### 自测要求

- 打开 `#/public/classes`，滚动到底部确认 FAQ 可见

### 验收标准

1. 看板底部有浅蓝背景 FAQ 区域，5 条内容完整
2. 3 列网格，640px 以下变 1 列

---

## F10：空状态与错误状态统一

修改文件：`js/app.js`, `css/styles.css`

### 实现要点

- 新增 `emptyStateHtml(title, description)` 和 `errorStateHtml(message)` 通用函数
- 空状态：居中 + CSS 空盒子图标 + 标题 + 说明
- 错误状态：居中 + 红色感叹号图标 + 错误信息 + 返回按钮
- 替换所有页面的空/错误渲染

### 自测要求

- 重启后端清空数据，打开前台看板确认空状态
- 访问不存在课程 ID 确认错误状态

### 验收标准

1. 空状态有图标 + 标题 + 说明，错误状态有图标 + 信息 + 返回按钮
2. 所有页面统一使用，图标 CSS 绘制不依赖图片

---

## 执行总览

| 编号 | 任务名称 | 前置 |
|---|---|---|
| F1 | Toast 通知组件 | 无 |
| F2 | 前台课程详情页完整重设计 | 无 |
| F3 | 报名表单体验增强 | 无 |
| F4 | 报名成功页重设计 | 无 |
| F5 | 后台课程创建/编辑表单重设计 | F1 |
| F6 | 后台课程详情页完整重设计 | F1 |
| F7 | 后台报名管理列表页重设计 | F1 |
| F8 | 后台报名详情页重设计 | F1 |
| F9 | 前台看板 FAQ 区域 | 无 |
| F10 | 空状态与错误状态统一 | 无 |

推荐执行顺序：F1 → F10 → F2 → F3 → F4 → F9 → F5 → F6 → F7 → F8

---

## 全量验收

```
1. 前台看板：课程卡片 + 底部 FAQ
2. 前台详情：hero + 适合对象 + 目标 + 规则 + FAQ + 底部 CTA
3. 报名表单：三组分段 + 必填标识 + loading 态
4. 报名成功：绿色勾 + 报名信息 + 后续说明
5. 后台创建：三组表单 + toast
6. 后台编辑：回填 + toast
7. 后台详情：指标 + facts + 规则 + 审核 + toast
8. 报名列表：卡片 + 统计 + 颜色 chip
9. 报名详情：信息 + 备注 toast + 状态 toast
10. 空/错误状态统一
11. 640px 可用
12. 无 window.alert
```
