param(
  [int]$FrontendPort = 5173,
  [int]$BackendPort = 18000,
  [string]$UvBin = "uv"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$python = "D:\software\anacond\python.exe"

if (-not (Test-Path $python)) {
  throw "Python not found: $python"
}

$frontCmd = "cd /d $root\apps\group_class_frontend && `"$python`" -m http.server $FrontendPort"
$backCmd = "cd /d $root && set PYTHONPATH=$root&& `"$UvBin`" run uvicorn apps.group_class_backend.app:app --host 0.0.0.0 --port $BackendPort"

$frontProc = Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $frontCmd -PassThru
$backProc = Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $backCmd -PassThru

Start-Sleep -Seconds 2

Write-Host "Frontend PID: $($frontProc.Id)"
Write-Host "Backend PID : $($backProc.Id)"
Write-Host "Frontend URL: http://127.0.0.1:$FrontendPort/"
Write-Host "Backend URL : http://127.0.0.1:$BackendPort/"
Write-Host ""
Write-Host "If frontend should call backend:"
Write-Host "localStorage.setItem('GROUP_CLASS_API_BASE_URL', 'http://127.0.0.1:$BackendPort'); location.reload();"
