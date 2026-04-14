# 前端开发与启动说明（MVP）

## 1. 实现范围（对齐文档）

本次前端开发对齐以下文档要点：

- `docs/plans/2026-04-11-group-class-kanban-ui-design.md` 的前台看板/详情/报名和后台课程管理列表（6.1~6.6）
- `docs/plans/2026-04-11-group-class-kanban-architecture-design.md` 的前台/后台接口契约（13.3、13.4）

已实现目录：

- `apps/group_class_frontend/index.html`
- `apps/group_class_frontend/css/styles.css`
- `apps/group_class_frontend/js/app.js`
- `apps/group_class_frontend/js/api.js`

## 2. 本地启动

在项目根目录执行：

```powershell
cd apps/group_class_frontend
python -m http.server 5173
```

浏览器访问：

```text
http://localhost:5173
```

## 3. 页面路由

- 前台看板：`#/public/classes`
- 课程详情：`#/public/classes/{classId}`
- 报名/候补：`#/public/enroll/{classId}?type=ENROLLMENT|WAITLIST|TRIAL`
- 后台课程管理列表：`#/admin/classes`

## 4. API 对接方式

默认请求同源 API（`/api/v1/...`）。  
如果后端是独立域名/端口，先在浏览器控制台设置：

```js
localStorage.setItem("GROUP_CLASS_API_BASE_URL", "http://localhost:8000");
location.reload();
```

当前后端接口不存在或不可达时，前端会自动回退到内置 mock 数据，便于先做页面联调与交互验证。

## 5. 已落地的前端规则

- 状态标签与 CTA：按状态渲染主按钮（立即报名/加入候补）
- 报名表单：必填校验 + 手机号格式校验（11位手机号）
- 提交保护：提交中禁用按钮，避免重复提交
- 详情页信息层次：课程摘要、适合对象、规则说明、FAQ摘要
- 后台列表：课程状态、人数、截止时间、动作字段展示
