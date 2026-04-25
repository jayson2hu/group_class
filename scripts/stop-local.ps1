$ports = @(5173, 18000)

foreach ($port in $ports) {
  $lines = netstat -ano | Select-String ":$port" | Select-String "LISTENING"
  foreach ($line in $lines) {
    $targetPid = ($line -split "\s+")[-1]
    if ($targetPid -match "^\d+$") {
      Stop-Process -Id ([int]$targetPid) -Force -ErrorAction SilentlyContinue
      Write-Host "Stopped PID $targetPid on port $port"
    }
  }
}
