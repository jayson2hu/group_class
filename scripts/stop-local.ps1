$ports = @(5173, 18000)

foreach ($port in $ports) {
  $lines = netstat -ano | Select-String ":$port" | Select-String "LISTENING"
  foreach ($line in $lines) {
    $pid = ($line -split "\s+")[-1]
    if ($pid -match "^\d+$") {
      Stop-Process -Id [int]$pid -Force -ErrorAction SilentlyContinue
      Write-Host "Stopped PID $pid on port $port"
    }
  }
}
