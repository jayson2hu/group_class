param(
  [int]$FrontendPort = 5173,
  [int]$BackendPort = 18000
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$python = "D:\software\anacond\python.exe"
$runtimeDir = Join-Path $root ".runtime"

if (-not (Test-Path $python)) {
  throw "Python not found: $python"
}

# Ensure old listeners are cleaned to avoid stale service behavior.
$ports = @($FrontendPort, $BackendPort)
foreach ($port in $ports) {
  $lines = netstat -ano | Select-String ":$port" | Select-String "LISTENING"
  foreach ($line in $lines) {
    $targetPid = ($line -split "\s+")[-1]
    if ($targetPid -match "^\d+$") {
      Stop-Process -Id ([int]$targetPid) -Force -ErrorAction SilentlyContinue
      Write-Host "Stopped stale PID $targetPid on port $port"
    }
  }
}

if (-not (Test-Path $runtimeDir)) {
  New-Item -ItemType Directory -Path $runtimeDir | Out-Null
}

$frontOut = Join-Path $runtimeDir "frontend.out.log"
$frontErr = Join-Path $runtimeDir "frontend.err.log"
$backOut = Join-Path $runtimeDir "backend.out.log"
$backErr = Join-Path $runtimeDir "backend.err.log"

Remove-Item $frontOut, $frontErr, $backOut, $backErr -ErrorAction SilentlyContinue

$frontProc = Start-Process `
  -FilePath $python `
  -ArgumentList "-m", "http.server", "$FrontendPort" `
  -WorkingDirectory (Join-Path $root "apps\group_class_frontend") `
  -RedirectStandardOutput $frontOut `
  -RedirectStandardError $frontErr `
  -PassThru

$backCmd = "set PYTHONPATH=$root&& set GROUP_CLASS_BACKEND_PORT=$BackendPort&& `"$python`" -m apps.group_class_backend.server"
$backProc = Start-Process `
  -FilePath "cmd.exe" `
  -ArgumentList "/c", $backCmd `
  -WorkingDirectory $root `
  -RedirectStandardOutput $backOut `
  -RedirectStandardError $backErr `
  -PassThru

Start-Sleep -Seconds 2

function Test-PortListening([int]$Port) {
  $lines = netstat -ano | Select-String ":$Port" | Select-String "LISTENING"
  return ($null -ne $lines -and $lines.Count -gt 0)
}

$frontOk = Test-PortListening -Port $FrontendPort
$backOk = Test-PortListening -Port $BackendPort

if (-not $frontOk -or -not $backOk) {
  Write-Host "Frontend started: $frontOk"
  Write-Host "Backend started : $backOk"
  Write-Host ""
  Write-Host "---- frontend.err.log ----"
  if (Test-Path $frontErr) { Get-Content $frontErr } else { Write-Host "(empty)" }
  Write-Host "---- backend.err.log ----"
  if (Test-Path $backErr) { Get-Content $backErr } else { Write-Host "(empty)" }
  throw "Startup failed. Check logs under $runtimeDir"
}

Write-Host "Frontend PID: $($frontProc.Id)"
Write-Host "Backend PID : $($backProc.Id)"
Write-Host "Frontend URL: http://127.0.0.1:$FrontendPort/"
Write-Host "Backend URL : http://127.0.0.1:$BackendPort/"
Write-Host ""
Write-Host "Logs:"
Write-Host "  $frontOut"
Write-Host "  $frontErr"
Write-Host "  $backOut"
Write-Host "  $backErr"
Write-Host ""
Write-Host "If frontend should call backend:"
Write-Host "localStorage.setItem('GROUP_CLASS_API_BASE_URL', 'http://127.0.0.1:$BackendPort'); location.reload();"
