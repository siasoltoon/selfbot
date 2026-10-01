param(
  [string]$Target = "100.114.8.105",
  [int]$Port = 1433,
  [int]$IntervalSeconds = 15,
  [string]$OutputPath = "runtime-network-probe.log"
)

$ErrorActionPreference = "Continue"

function Write-ProbeLog {
  param([string]$Message)
  $line = "$(Get-Date -Format o) $Message"
  Add-Content -Path $OutputPath -Value $line -Encoding utf8
}

Write-ProbeLog "PROBE_START target=$Target port=$Port interval_seconds=$IntervalSeconds"

while ($true) {
  $timestamp = Get-Date -Format o

  try {
    $tcp = Test-NetConnection -ComputerName $Target -Port $Port -InformationLevel Detailed -WarningAction SilentlyContinue
    Write-ProbeLog (
      "TCP timestamp=$timestamp success=$($tcp.TcpTestSucceeded) " +
      "remote=$($tcp.RemoteAddress):$($tcp.RemotePort) " +
      "source=$($tcp.SourceAddress) ping=$($tcp.PingSucceeded)"
    )
  } catch {
    Write-ProbeLog "TCP timestamp=$timestamp success=ERROR type=$($_.Exception.GetType().Name)"
  }

  $tailscale = Get-Command tailscale -ErrorAction SilentlyContinue
  if ($tailscale) {
    try {
      $pingOutput = tailscale ping --timeout=5s $Target 2>&1 | Out-String
      $summary = ($pingOutput -replace "[\r\n]+", " ").Trim()
      if ($summary.Length -gt 300) {
        $summary = $summary.Substring(0, 300)
      }
      Write-ProbeLog "TAILSCALE timestamp=$timestamp result=$summary"
    } catch {
      Write-ProbeLog "TAILSCALE timestamp=$timestamp result=ERROR type=$($_.Exception.GetType().Name)"
    }
  } else {
    Write-ProbeLog "TAILSCALE timestamp=$timestamp result=CLI_NOT_FOUND"
  }

  Start-Sleep -Seconds $IntervalSeconds
}
