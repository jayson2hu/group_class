# 本地启动说明（group_class）

## 1. 当前可启动内容（FastAPI 迁移后）

当前仓库已具备最小可运行的前后端联调能力：

- 后端 API 入口：`apps/group_class_backend/app.py`
- 前端页面入口：`apps/group_class_frontend/index.html`
- 后端测试：`tests/group_class_backend/`

## 2. 启动后端

在仓库根目录执行：

```powershell
uv run uvicorn apps.group_class_backend.app:app --host 0.0.0.0 --port 18000 --reload
```

后端地址：

```text
http://127.0.0.1:18000
```

## 3. 启动前端

打开另一个终端执行：

```powershell
cd apps/group_class_frontend
& 'D:/software/anacond/python.exe' -m http.server 5173
```

前端地址：

```text
http://127.0.0.1:5173
```

## 4. 前后端联调设置

前端默认请求同源 `/api/v1/...`。跨端口联调时在浏览器控制台设置：

```js
localStorage.setItem("GROUP_CLASS_API_BASE_URL", "http://127.0.0.1:18000");
location.reload();
```

## 5. 自测命令

后端自动化测试：

```powershell
uv run pytest tests/ -q
```

联调与问题记录见：`docs/integration-selftest-2026-04-13.md`。

## 6. Linux/macOS 与容器化

请参考统一文档：`docs/development-and-deployment.md`。
