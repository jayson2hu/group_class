# group_class 部署与开发指南

## 1. 适用范围

本文档用于本仓库的本地开发、联调验证和交付前检查。

仓库根目录：`d:/vscodefile/group_class`

## 2. 环境要求

- Windows（PowerShell）或 Linux/macOS（bash）
- Python 3.12+
- Node.js（用于前端静态检查，可选）
- Docker / Docker Compose（容器化部署可选）

## 3. 目录说明

- 后端：`apps/group_class_backend/`
- 前端：`apps/group_class_frontend/`
- 测试：`tests/group_class_backend/`
- 脚本：
  - Windows：`scripts/start-local.ps1`、`scripts/stop-local.ps1`
  - Linux/macOS：`scripts/start-local.sh`、`scripts/stop-local.sh`
- 计划/验收：`docs/plans/`

## 4. 一键本地启动

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1
```

默认端口：

- 前端：`5173`
- 后端：`18000`

访问地址：

- `http://127.0.0.1:5173/`
- `http://127.0.0.1:18000/`

停止：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop-local.ps1
```

## 5. 手动启动（不使用脚本）

### 5.1 启动后端

```powershell
$env:PYTHONPATH='d:/vscodefile/group_class'
$env:GROUP_CLASS_BACKEND_PORT='18000'
& 'D:/software/anacond/python.exe' -m apps.group_class_backend.server
```

### 5.2 启动前端

```powershell
cd apps/group_class_frontend
& 'D:/software/anacond/python.exe' -m http.server 5173
```

## 6. Linux/macOS 启动（脚本）

```bash
chmod +x scripts/start-local.sh scripts/stop-local.sh
./scripts/start-local.sh
```

停止：

```bash
./scripts/stop-local.sh
```

可选环境变量：

```bash
PYTHON_BIN=python3 FRONTEND_PORT=5173 BACKEND_PORT=18000 ./scripts/start-local.sh
```

## 7. 容器化部署（Docker Compose）

### 7.1 启动

```bash
docker compose up -d --build
```

### 7.2 访问

- 前端：`http://127.0.0.1:5173/`
- 后端：`http://127.0.0.1:18000/`

### 7.3 停止

```bash
docker compose down
```

### 7.4 容器说明

- `backend`：`docker/backend.Dockerfile`，运行 `apps.group_class_backend.server`
- `frontend`：`docker/frontend.Dockerfile`，使用 nginx 托管前端静态文件

## 8. 前后端联调

当前前端默认 API 基址为：

- `http://127.0.0.1:18000`

如果浏览器里曾改过 API 地址，建议清理：

```js
localStorage.removeItem("GROUP_CLASS_API_BASE_URL");
location.reload();
```

## 9. 开发流程建议

1. 拉代码后先运行后端测试
2. 启动前后端并手动走关键链路
3. 修改后执行静态检查与回归
4. 更新对应计划文档中的“开发进度与验收记录”

## 10. 测试与验收

### 8.1 后端回归

```powershell
$env:PYTHONPATH='d:/vscodefile/group_class'
& 'D:/software/anacond/python.exe' -m pytest tests/group_class_backend -q
```

### 8.2 前端语法检查

```powershell
node --check apps/group_class_frontend/js/api.js
node --check apps/group_class_frontend/js/app.js
```

### 8.3 联调冒烟

- 打开前台看板：`#/public/classes`
- 打开后台课程：`#/admin/classes`（先切换管理员）
- 验证报名与后台报名管理链路

## 11. 发布前检查清单

- 后端测试通过
- 前端无语法错误
- 关键页面 640px 下可用
- 文档更新到最新（README + 对应计划文档）
- 无临时文件提交（如 `__pycache__`、`.pyc`）

## 12. 常见问题

### 10.1 Failed to fetch

通常是前端请求地址和后端端口不一致。确认：

- 后端已启动在 `18000`
- `GROUP_CLASS_API_BASE_URL` 未被旧值污染

### 10.2 启动后端失败（python 不可执行）

检查脚本中的 Python 路径是否存在：

- `scripts/start-local.ps1`
- `docs/local-startup-guide.md`

### 10.3 Git 推送后只有 README

说明代码目录未 add/commit。执行：

```powershell
git add .
git commit -m "chore: sync code and docs"
git push origin main
```

### 12.4 Linux 启动脚本执行失败

- 先确认执行权限：`chmod +x scripts/start-local.sh scripts/stop-local.sh`
- 确认 `PYTHON_BIN` 可执行：`python3 --version`

### 12.5 Docker compose 启动失败

- 先执行 `docker --version` 和 `docker compose version`
- 如果端口冲突，修改 `docker-compose.yml` 端口映射后重启
