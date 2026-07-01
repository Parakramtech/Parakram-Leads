# Parakram VPS — installs and starts the dashboard Windows service via WinSW.
# Run as a deferred, elevated MSI custom action from the DASHBOARD_DIR.
#
# A plain Node.js/Express process cannot be registered directly with
# `sc create` — Windows services must speak the Service Control Manager
# handshake, which Node does not implement. WinSW (bundled as
# ParakramVPS-svc.exe + ParakramVPS-svc.xml) wraps the Node process and
# speaks that protocol for us.

$ErrorActionPreference = "Continue"
$dir = $PSScriptRoot
$svc = Join-Path $dir "ParakramVPS-svc.exe"

$logDir = Join-Path $env:ProgramData "ParakramVPS"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$logFile = Join-Path $logDir "install-service.log"
function Write-Log([string]$msg) {
    Add-Content -Path $logFile -Value ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg)
}

function Run-Capture([string]$exe, [string]$argString) {
    $stdout = Join-Path $env:TEMP ("pvps-out-{0}.txt" -f ([guid]::NewGuid()))
    $stderr = Join-Path $env:TEMP ("pvps-err-{0}.txt" -f ([guid]::NewGuid()))
    try {
        $p = Start-Process -FilePath $exe -ArgumentList $argString -NoNewWindow -Wait -PassThru `
            -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $out = (Get-Content $stdout -Raw -ErrorAction SilentlyContinue)
        $err = (Get-Content $stderr -Raw -ErrorAction SilentlyContinue)
        Write-Log "RUN: $exe $argString => exit=$($p.ExitCode)"
        if ($out) { Write-Log "  stdout: $($out.Trim())" }
        if ($err) { Write-Log "  stderr: $($err.Trim())" }
        return $p.ExitCode
    } finally {
        Remove-Item $stdout, $stderr -ErrorAction SilentlyContinue
    }
}

Write-Log "=== install-service.ps1 started ==="
Write-Log "WinSW=$svc dir=$dir"

$existingExit = Run-Capture "sc.exe" "query ParakramVPS"
if ($existingExit -eq 0) {
    Write-Log "Service exists; stopping and uninstalling before recreate"
    Run-Capture $svc "stop" | Out-Null
    Start-Sleep -Seconds 2
    Run-Capture $svc "uninstall" | Out-Null
    Start-Sleep -Seconds 1
}

Run-Capture $svc "install"
Start-Sleep -Seconds 1
$startExit = Run-Capture $svc "start"
Write-Log "Service start exit=$startExit"

Remove-NetFirewallRule -DisplayName "Parakram VPS Dashboard" -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "Parakram VPS Dashboard" -Direction Inbound -Protocol TCP `
    -LocalPort 9876 -Action Allow -Profile Any -ErrorAction SilentlyContinue | Out-Null

Write-Log "=== install-service.ps1 complete ==="
exit 0
