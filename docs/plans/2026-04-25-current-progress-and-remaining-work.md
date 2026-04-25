# 拼课课程系统当前进度与剩余工作

Date: 2026-04-25
Status: MVP 可联调 / 可演示
Owner: Codex

## 1. 当前结论

当前项目已经完成拼课课程系统的 MVP 主链路：管理员登录后可创建课程、编辑课程、提交审核、审核通过；课程可在前台看板展示；家长可提交报名；后台可查看报名、维护跟进备注并更新报名状态。

自动化检查结果：

- 后端测试：`python -m pytest tests/group_class_backend -q` -> `91 passed`
- 前端语法检查：`node --check apps/group_class_frontend/js/api.js` -> 通过
- 前端语法检查：`node --check apps/group_class_frontend/js/app.js` -> 通过

## 2. 已完成范围

### 2.1 后端

- 课程模型、报名模型、课程模板模型已建立。
- 支持 DRAFT 创建、课程编辑、课程详情、课程列表。
- 支持审核流：`submit-review`、`approve`、`reject`。
- 支持前台课程可见性过滤。
- 支持报名提交：报名、候补、试听三类。
- 支持后台报名管理：列表、详情、备注更新、状态更新。
- 支持登录接口：`POST /api/v1/auth/login`。
- 后台接口已增加 Bearer token 校验。
- SQLite 仓储、schema 和约束已有测试覆盖。

### 2.2 前端

- 前台课程看板、课程详情、报名表单、报名成功页已完成。
- 后台登录页与认证流程已完成。
- 后台课程列表、详情、新建、编辑页面已完成。
- 后台审核操作入口已完成。
- 后台报名列表、报名详情、备注和状态管理已完成。
- 导航已区分公开入口和登录后的后台入口。
- 全量视觉重设计已落地，统一按钮、表格、表单、状态、toast 和响应式样式。

### 2.3 工程与启动

- Windows / Linux 本地启动脚本已存在。
- Docker Compose、前后端 Dockerfile、nginx 配置已存在。
- README 和开发/部署文档已提供基本入口。

## 3. 本次提交对应变更

- 后端新增演示登录用户、token 会话和后台接口鉴权。
- 后端新增 `UNAUTHORIZED` 错误码映射。
- 前端新增登录页、登录态持久化、后台路由守卫和退出登录。
- 前端后台课程与报名管理页面继续适配新设计系统。
- 前端 API 客户端补齐认证请求头和后台管理方法。
- 本地启动/停止脚本增强。
- 新增 full redesign 任务记录文档。
- 新增当前进度和剩余工作记录文档。
- `.gitignore` 排除本地运行日志、`.runtime/` 和 `.claude/` 私有配置。

## 3.1 2026-04-25 前端文案清洗进展

- 已新增计划与验收文档：`docs/plans/2026-04-25-frontend-copy-cleanup-plan.md`
- 已清洗前端入口、核心页面渲染文案和 mock 数据：
  - `apps/group_class_frontend/index.html`
  - `apps/group_class_frontend/js/app.js`
  - `apps/group_class_frontend/js/api.js`
- 自测结果：
  - `node --check apps/group_class_frontend/js/api.js` -> 通过
  - `node --check apps/group_class_frontend/js/app.js` -> 通过
  - `python -m pytest tests/group_class_backend -q` -> `91 passed`
  - Unicode 码点检查未发现典型 mojibake 字符残留

## 4. 仍未完成

### 4.1 P0 后续收尾

- 浏览器端完整人工回归或 E2E 自动化尚未补齐。
- 前端入口、核心页面和 mock 数据的历史中文文案已清洗；仍建议做一次浏览器 UI 走查确认实际渲染。
- 后台鉴权目前是演示级 token，会话保存在内存中，不适合生产环境。

### 4.2 MVP 增强

- server runtime 仍使用 InMemory repository，尚未接入 SQLite 或真实数据库。
- 列表分页参数尚未完整从 HTTP 和前端 UI 透传。
- 前端缺少课程/报名搜索、筛选和分页控件。
- 报名成功页还可以展示更完整的课程状态和后续通知说明。
- 候补表单尚未独立成差异化页面。

### 4.3 运营能力

- 模板 CRUD 接口和模板管理页面尚未完成。
- 报名名单导出尚未完成。
- 课程下架、取消、删除能力尚未完成。
- 候补转正流程尚未完成。
- 报名转其他课程尚未完成。
- 自动状态计算尚未完成，例如即将成班、满员、报名截止自动关闭。

### 4.4 生产化能力

- 正式用户体系、密码存储、权限模型和 token 生命周期尚未完成。
- 审计日志目前为 NullAuditWriter，尚未持久化。
- 自动通知、支付状态、支付锁位尚未完成。
- 监控、错误上报、部署环境变量和数据备份策略尚未完成。

## 5. 建议下一步

1. 先做一次浏览器人工回归，覆盖登录、建课、编辑、提审、审核、报名、报名管理。
2. 清洗前端历史中文文案，避免演示时出现乱码。
3. 将 server runtime 从 InMemory 切换到 SQLite，形成可保留数据的本地演示环境。
4. 补齐后台列表分页、搜索和筛选。
5. 再推进模板管理、导出、课程下架/取消等运营功能。
