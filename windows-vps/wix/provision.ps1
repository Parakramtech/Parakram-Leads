# Parakram VPS — Provisioning Script
# Runs as a deferred, elevated MSI custom action during install.
# Idempotent: safe to re-run on repair/upgrade. Never aborts the MSI on
# a non-critical failure — degrades gracefully and logs everything.

$ErrorActionPreference = "Continue"
$logDir = Join-Path $env:ProgramData "ParakramVPS"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$logFile = Join-Path $logDir "provision.log"

function Write-Log([string]$msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $logFile -Value $line
}

Write-Log "=== Provisioning started ==="

# ── 1. OpenSSH Server (idempotent) ──────────────────────────────────────
try {
    $svc = Get-Service sshd -ErrorAction SilentlyContinue
    if (-not $svc) {
        Write-Log "OpenSSH.Server capability not present; installing..."
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 -ErrorAction Stop | Out-Null
        Write-Log "OpenSSH.Server capability installed"
        $svc = Get-Service sshd -ErrorAction SilentlyContinue
    }
    if ($svc) {
        $sshdConfigDir = Join-Path $env:ProgramData "ssh"
        New-Item -ItemType Directory -Path $sshdConfigDir -Force | Out-Null
        $sshdConfig = @"
Port 22
Protocol 2
PubkeyAuthentication yes
PasswordAuthentication yes
PermitEmptyPasswords no
MaxAuthTries 3
MaxSessions 10
ClientAliveInterval 300
ClientAliveCountMax 2
Subsystem sftp sftp-server.exe
AllowTcpForwarding yes
GatewayPorts yes
X11Forwarding no
"@
        Set-Content -Path (Join-Path $sshdConfigDir "sshd_config") -Value $sshdConfig -Force -Encoding ASCII
        & ssh-keygen.exe -A 2>$null | Out-Null
        Set-Service -Name sshd -StartupType Automatic -ErrorAction SilentlyContinue
        Start-Service -Name sshd -ErrorAction SilentlyContinue
        Set-Service -Name ssh-agent -StartupType Automatic -ErrorAction SilentlyContinue
        Start-Service -Name ssh-agent -ErrorAction SilentlyContinue
        Write-Log "OpenSSH Server configured and started"
    } else {
        Write-Log "WARNING: OpenSSH Server unavailable on this system (may need Windows Update); skipping"
    }
} catch {
    Write-Log "WARNING: OpenSSH provisioning failed: $_"
}

# ── 2. Cloudflare Tunnel binary (bundled, zero download needed) ────────
try {
    $installDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $cloudflared = Join-Path $installDir "cloudflared.exe"
    if (Test-Path $cloudflared) {
        Write-Log "cloudflared.exe present at $cloudflared (bundled, no download required)"
    } else {
        Write-Log "WARNING: cloudflared.exe not found in install directory"
    }
} catch {
    Write-Log "WARNING: cloudflared check failed: $_"
}

# ── 3. Windows Firewall rules (idempotent) ──────────────────────────────
try {
    Start-Service -Name MpsSvc -ErrorAction SilentlyContinue
    $rules = @(
        @{ Name = "Parakram VPS Dashboard"; Port = 9876 },
        @{ Name = "Parakram VPS SSH"; Port = 22 }
    )
    foreach ($rule in $rules) {
        Remove-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue
        New-NetFirewallRule -DisplayName $rule.Name -Direction Inbound -Protocol TCP `
            -LocalPort $rule.Port -Action Allow -Profile Any -ErrorAction SilentlyContinue | Out-Null
    }
    Write-Log "Firewall rules configured (9876, 22)"
} catch {
    Write-Log "WARNING: Firewall configuration failed: $_"
}

Write-Log "=== Provisioning complete ==="
exit 0
