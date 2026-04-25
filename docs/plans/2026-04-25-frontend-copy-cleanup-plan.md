# 前端中文文案清洗计划

Date: 2026-04-25
Status: Completed
Owner: Codex

## 1. 背景

当前前端核心功能已经可联调，但历史页面文案存在 mojibake 乱码，影响演示和人工回归判断。本轮只处理前端显示文案和相关 mock 数据，不扩大业务范围。

## 2. 范围

计划修改：

- `apps/group_class_frontend/index.html`
- `apps/group_class_frontend/js/app.js`
- `apps/group_class_frontend/js/api.js`
- 本计划文档和当前进度文档

不处理：

- 后端持久化改造
- 正式鉴权体系
- 模板 CRUD
- 报名导出
- 搜索、筛选、分页

## 3. 实施计划

1. 定位前端乱码字段和页面范围。
2. 清洗顶部导航、公共看板、课程详情、报名表单、成功页、登录页、后台课程管理、后台报名管理等页面文案。
3. 清洗 mock 数据中的课程、报名和状态标签。
4. 保持现有路由、API 调用和 DOM 事件绑定不变。
5. 运行前端语法检查和后端回归测试。
6. 更新本计划文档和当前进度文档。

## 4. 验收标准

- `index.html` 页面标题、导航和按钮不再出现明显乱码。
- `app.js` 核心页面文案不再出现明显乱码。
- `api.js` mock 数据不再出现明显乱码。
- `node --check apps/group_class_frontend/js/api.js` 通过。
- `node --check apps/group_class_frontend/js/app.js` 通过。
- `python -m pytest tests/group_class_backend -q` 通过，确认后端行为未回退。
- 本文档记录最终自测结果和剩余风险。

## 5. 自测记录

已执行：

- `node --check apps/group_class_frontend/js/api.js` -> 通过
- `node --check apps/group_class_frontend/js/app.js` -> 通过
- `python -m pytest tests/group_class_backend -q` -> `91 passed`
- Unicode 码点检查：
  - `apps/group_class_frontend/index.html` 无 `U+00C3/U+00C2/U+FFFD` 等典型 mojibake 字符残留
  - `apps/group_class_frontend/js/app.js` 无 `U+00C3/U+00C2/U+FFFD` 等典型 mojibake 字符残留
  - `apps/group_class_frontend/js/api.js` 无 `U+00C3/U+00C2/U+FFFD` 等典型 mojibake 字符残留

## 6. 验收结论

通过。前端入口、核心页面文案和 mock 数据已清洗为 UTF-8 中文，保留原有路由和 API 调用结构。

## 7. 剩余风险

- 当前环境未发现 Playwright 或浏览器 E2E 依赖，本轮未执行浏览器截图级自动化回归。
- PowerShell 当前控制台会把中文输出显示为乱码，但文件本身已通过 UTF-8 读取和 Unicode 检查。
