# 联调与自测记录（2026-04-13）

> 历史记录：本文记录 2026-04-13 旧 `server.py` 手写 HTTP 服务时期的联调结果。FastAPI 迁移后当前后端入口已变更为 `apps.group_class_backend.app:app`。

## 1. 目标

- 完成前端 `apps/group_class_frontend/` 与后端 `apps/group_class_backend/server.py` 联调
- 执行后端自动化测试，确认无回归
- 记录联调过程中发现的问题与处理方式

## 2. 联调环境

- OS: Windows
- Python: `D:/software/anacond/python.exe`
- Backend: `http://127.0.0.1:18000`
- Frontend: `http://127.0.0.1:5173`

## 3. 联调步骤与结果

### 3.1 前端可访问性

- 请求：`GET http://127.0.0.1:5173/index.html`
- 结果：`200 OK`

### 3.2 公共课程列表

- 请求：`GET /api/v1/public/classes`
- 结果：成功，`data.total=2`

### 3.3 课程详情

- 请求：`GET /api/v1/public/classes/{classId}`
- 结果：成功，返回课程详情（含状态、人数、规则字段）

### 3.4 报名提交

- 请求：`POST /api/v1/public/registrations`
- 结果：成功，`registrationStatus=SUBMITTED`

### 3.5 后台课程列表

- 请求：`GET /api/v1/admin/classes`
- 结果：成功，`data.total=3`

### 3.6 CORS 预检

- 请求：`OPTIONS /api/v1/public/registrations`
- 结果：`204`，跨域响应头正常返回

### 3.7 自动化测试

- 命令：`$env:PYTHONPATH='d:/vscodefile/group_class'; pytest -q tests/group_class_backend`
- 结果：`91 passed`

## 4. 问题记录（含处理）

### ISSUE-001：`python` 启动命令不可用

- 现象：`Start-Process -FilePath python` 失败（Windows Store alias 限制）
- 原因：系统 `python.exe` 指向 `WindowsApps` 别名，不可直接用于该启动方式
- 处理：统一改为显式解释器路径 `D:/software/anacond/python.exe`
- 状态：已解决

### ISSUE-002：`8000` 端口已被占用

- 现象：本机已有进程监听 `127.0.0.1:8000`
- 影响：后端默认端口冲突
- 处理：联调改用 `18000` 端口启动后端
- 状态：已解决

### ISSUE-003：`Invoke-WebRequest` 需要 `UseBasicParsing`

- 现象：PowerShell 调用网页时报 IE 引擎不可用错误
- 处理：命令增加 `-UseBasicParsing`
- 状态：已解决

## 5. 当前结论

- 前后端 MVP 已可本地启动并完成基本链路联调
- 后端原有测试全部通过，无回归
- 当前已形成可复现启动与联调路径，可继续进入功能增强或真实后端接口扩展
