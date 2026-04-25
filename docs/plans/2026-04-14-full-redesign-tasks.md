# 2026-04-14 Full Redesign Tasks
Date: 2026-04-14
Owner: Codex
Status: Completed

## 目标
- 按 R1-R18 实施全量重设计与登录认证改造。
- 完成自测与验收，形成可追溯记录。

## 变更范围
- 后端：`apps/group_class_backend/server.py`, `apps/group_class_backend/common/error_codes.py`
- 前端：`apps/group_class_frontend/index.html`, `apps/group_class_frontend/js/api.js`, `apps/group_class_frontend/js/app.js`, `apps/group_class_frontend/css/styles.css`

## 任务进度（R1-R18）
| 编号 | 任务 | 结果 | 说明 |
|---|---|---|---|
| R1 | 设计系统重置（CSS变量+去渐变） | ✅ 完成 | 新增靛蓝主题变量，统一纯色底、轻阴影、8px圆角；覆盖旧渐变背景 |
| R2 | Topbar + 导航重设计 | ✅ 完成 | 顶栏/导航扁平化；移除旧角色切换按钮 |
| R3 | 通用组件样式（按钮/chip/表格/表单） | ✅ 完成 | 按钮、chip、table、form 统一样式规范 |
| R4 | Toast 样式适配 | ✅ 完成 | 改为纯色卡片+左侧语义色，动画改为 opacity fade |
| R5 | 后端登录接口 | ✅ 完成 | 新增 `POST /api/v1/auth/login` 与 3 个预设用户 |
| R6 | 前端登录页 + 认证流程 | ✅ 完成 | 新增 `#/login`、登录表单、token 存储、后台守卫、退出登录 |
| R7 | 前台页面重设计-列表 | ✅ 完成 | 保留信息架构并套用新设计系统 |
| R8 | 前台页面重设计-详情 | ✅ 完成 | 详情信息区、规则区、FAQ、底部 CTA 与新视觉统一 |
| R9 | 前台页面重设计-报名 | ✅ 完成 | 表单分组与按钮状态沿用并统一视觉 |
| R10 | 前台页面重设计-成功页 | ✅ 完成 | 成功反馈卡片与行为按钮统一 |
| R11 | 后台页面重设计-课程列表 | ✅ 完成 | 列表与卡片视觉统一 |
| R12 | 后台页面重设计-课程详情 | ✅ 完成 | 指标区、信息区、操作区统一 |
| R13 | 后台页面重设计-新建/编辑课程 | ✅ 完成 | 表单与分段样式统一 |
| R14 | 后台页面重设计-报名列表 | ✅ 完成 | 统计+列表卡片统一 |
| R15 | 后台页面重设计-报名详情 | ✅ 完成 | 信息展示/备注/状态区统一 |
| R16 | 空状态/错误状态统一 | ✅ 完成 | 全局 `emptyStateHtml/errorStateHtml` 统一样式 |
| R17 | 移动端响应式收尾 | ✅ 完成 | 保留并应用 900/640 断点规则 |
| R18 | 全量回归验收 | ✅ 完成 | 代码检查 + 后端测试 + 认证冒烟通过 |

## 接口契约（认证相关）
### 1) 登录
- `POST /api/v1/auth/login`
- Request:
```json
{ "username": "admin", "password": "123456" }
```
- Success `200`:
```json
{
  "code": "OK",
  "data": {
    "token": "tk-...",
    "actorId": "u_admin",
    "actorRoles": ["CLASS_ADMIN"],
    "displayName": "Admin"
  }
}
```
- Failure `401`:
```json
{
  "code": "UNAUTHORIZED",
  "details": [{ "field": "credentials", "message": "username or password is invalid" }]
}
```

### 2) 后台接口鉴权
- 所有 `/api/v1/admin/*` 必须携带：`Authorization: Bearer <token>`
- 缺失或非法 token 返回 `401 UNAUTHORIZED`
- `/api/v1/public/*` 不要求 token

## 自测记录
### A. 静态检查
```bash
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js
```
结果：通过。

### B. 后端自动化测试
```bash
D:/software/anacond/python.exe -m pytest tests/group_class_backend -q
```
结果：`91 passed`。

### C. 认证接口冒烟（本地）
执行结果：
- `LOGIN_OK=True`
- `LOGIN_BAD_401=True`
- `ADMIN_NO_TOKEN_401=True`
- `ADMIN_WITH_TOKEN_OK=True`
- `PUBLIC_NO_TOKEN_OK=True`

## 验收结论
- 功能：通过（登录、鉴权、前后台路由守卫、退出登录生效）。
- 视觉：通过（去渐变/去重阴影/去胶囊化，统一为靛蓝+纯色+8px+轻阴影）。
- 回归：通过（自动化与关键冒烟均通过）。
- 交付建议：可进入联调/演示。

## 已知说明
- 历史页面文案存在旧字符编码遗留，不影响功能与验收结论；后续可单独做一次文案清洗。
