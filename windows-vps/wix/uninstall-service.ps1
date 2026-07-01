# Parakram VPS — stops and removes the dashboard Windows service + firewall rule.
$ErrorActionPreference = "Continue"
$dir = $PSScriptRoot
$svc = Join-Path $dir "ParakramVPS-svc.exe"

if (Test-Path $svc) {
    & $svc stop 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    & $svc uninstall 2>&1 | Out-Null
} else {
    sc.exe stop ParakramVPS 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    sc.exe delete ParakramVPS 2>&1 | Out-Null
}
Remove-NetFirewallRule -DisplayName "Parakram VPS Dashboard" -ErrorAction SilentlyContinue

# Clean up WinSW-generated log files (not tracked as MSI components, so
# RemoveFiles/RemoveFolders won't touch them — remove explicitly for a
# truly clean uninstall with no leftover directory).
Start-Sleep -Seconds 1
Get-ChildItem -Path $dir -Filter "ParakramVPS-svc.*.log" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

exit 0
