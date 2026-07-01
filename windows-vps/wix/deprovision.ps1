# Parakram VPS — Deprovisioning Script
# Runs as a deferred, elevated MSI custom action during uninstall.
# Only removes what we added (firewall rules). Leaves OpenSSH Server
# installed since it's a general Windows capability, not exclusively ours.

$ErrorActionPreference = "Continue"
$logDir = Join-Path $env:ProgramData "ParakramVPS"
$logFile = Join-Path $logDir "provision.log"

function Write-Log([string]$msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    try { Add-Content -Path $logFile -Value $line -ErrorAction SilentlyContinue } catch {}
}

Write-Log "=== Deprovisioning started ==="

foreach ($name in @("Parakram VPS Dashboard", "Parakram VPS SSH")) {
    Remove-NetFirewallRule -DisplayName $name -ErrorAction SilentlyContinue
}
Write-Log "Firewall rules removed"
Write-Log "=== Deprovisioning complete ==="
exit 0
