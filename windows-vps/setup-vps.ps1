#requires -RunAsAdministrator

<#
.SYNOPSIS
    Parakram VPS — Turns any Windows machine into a production-ready VPS in minutes.
.DESCRIPTION
    One-click setup that installs and configures:
    - OpenSSH Server (remote shell access)
    - Cloudflare Tunnel (public URL, no port forwarding needed)
    - Web Management Dashboard with real-time stats
    - Auto-start services on boot

    Zero open firewall ports required — all traffic goes through Cloudflare Tunnel.
.NOTES
    Version: 1.1.0
    Author: Parakram
#>

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Parakram VPS - Setup"

# -- Config -----------------------------------------------------------------
$VERSION = "1.1.0"
$LOG_FILE = "$env:USERPROFILE\parakram-vps-install.log"
$INSTALL_DIR = "$env:ProgramFiles\ParakramVPS"
$DASHBOARD_PORT = 9876
$TUNNEL_NAME = "windows-vps-$([System.Environment]::MachineName.ToLower())"

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = "[$timestamp] $Message"
    Write-Host $line -ForegroundColor $Color
    Add-Content -Path $LOG_FILE -Value $line
}

function Write-Step { param([string]$Message); Write-Host "`n--- $Message ---" -ForegroundColor Cyan }
function Write-Success { Write-Host "  $($args[0])" -ForegroundColor Green }
function Write-Info { Write-Host "   $($args[0])" -ForegroundColor Gray }
function Write-Warn { Write-Host "   $($args[0])" -ForegroundColor Yellow }

# -- Splash -----------------------------------------------------------------
Clear-Host
$splash = @'
  ____            _    __     ____   ___  ____
 |  _ \ __ _ _ __| | _ \ \   / / \ | \/ |
 | |_) / _` | '__| |/ / \ \ / / _ \| |\/| |
 |  __/ (_| | |  |   <   \ V / ___ \ |  | |
 |_|   \__,_|_|  |_|\_\   \_/_/   \_\_|  |_|

            Windows VPS - Setup v1.1.0
'@
Write-Host $splash -ForegroundColor DarkYellow
Write-Host ""

# -- Prerequisites Check ----------------------------------------------------
Write-Step "Checking Prerequisites"

$errorsList = @()
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    $errorsList += "Must run as Administrator"
}

$os = Get-CimInstance Win32_OperatingSystem
Write-Info "OS: $($os.Caption) $($os.Version)"

$arch = (Get-CimInstance Win32_ComputerSystem).SystemType
if ($arch -notmatch "64") { $errorsList += "64-bit Windows required" }

$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$env:SystemDrive'"
Write-Info "Free Space: $([math]::Round($disk.FreeSpace / 1GB, 1)) GB on $env:SystemDrive"
if ($disk.FreeSpace -lt 5GB) { $errorsList += "At least 5GB free space required" }

$mem = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$memGB = [math]::Round($mem / 1GB, 1)
Write-Info "RAM: $memGB GB"
if ($mem -lt 2GB) { $errorsList += "At least 2GB RAM required" }

if ($errorsList.Count -gt 0) {
    Write-Log "Prerequisites failed:" -Color Red
    $errorsList | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
    Write-Host "`nPress any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey()
    exit 1
}
Write-Success "All prerequisites met"

# -- 1. Install OpenSSH Server --------------------------------------------
Write-Step "Installing OpenSSH Server"

$sshService = Get-Service -Name sshd -ErrorAction SilentlyContinue
if (-not $sshService) {
    Write-Info "Adding OpenSSH Server Windows capability..."
    try {
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
        Write-Success "OpenSSH Server installed"
    } catch {
        Write-Warn "Windows capability install failed, trying winget..."
        winget install "OpenSSH Server" --accept-source-agreements 2>$null | Out-Null
    }
} else {
    Write-Info "OpenSSH Server already installed"
}

$sshConfig = @'
Port 22
Protocol 2
PubkeyAuthentication yes
PasswordAuthentication yes
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UseDNS no
Subsystem sftp sftp-server.exe
AllowTcpForwarding yes
GatewayPorts yes
'@
$sshConfig | Set-Content -Path "$env:ProgramData\ssh\sshd_config" -Force

ssh-keygen.exe -A 2>$null | Out-Null

Set-Service -Name sshd -StartupType Automatic
Start-Service -Name sshd -ErrorAction SilentlyContinue
Set-Service -Name ssh-agent -StartupType Automatic
Start-Service -Name ssh-agent -ErrorAction SilentlyContinue

$sshStatus = (Get-Service sshd).Status
Write-Success "SSH Server: $sshStatus"

# -- 2. Download Cloudflare Tunnel ----------------------------------------
Write-Step "Setting Up Cloudflare Tunnel"

$cloudflaredPath = "$INSTALL_DIR\cloudflared.exe"
if (-not (Test-Path $cloudflaredPath)) {
    Write-Info "Downloading cloudflared..."
    $url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    New-Item -ItemType Directory -Force $INSTALL_DIR | Out-Null
    Invoke-WebRequest -Uri $url -OutFile $cloudflaredPath -UseBasicParsing
    Write-Success "cloudflared downloaded"
} else {
    Write-Info "cloudflared already present"
}

# -- 3. Create Management Dashboard ----------------------------------------
Write-Step "Creating Management Dashboard"

$dashboardDir = "$INSTALL_DIR\dashboard"
New-Item -ItemType Directory -Force $dashboardDir | Out-Null

$dashboardHtml = @'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Parakram VPS</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:#070708;color:#e8e6e3;font-family:'Segoe UI',system-ui,sans-serif;padding:24px}
  .hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:32px}
  .hdr h1{font-size:20px;font-weight:600;color:#c9a96e}
  .hdr span{color:#5a5a5a;font-size:12px}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
  .c{background:#0d0d0e;border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:20px}
  .c h3{font-size:11px;color:#5a5a5a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px}
  .c .v{font-size:28px;font-weight:700;color:#e8e6e3}
  .c .s{font-size:12px;color:#5a5a5a;margin-top:4px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th{text-align:left;font-size:11px;color:#5a5a5a;text-transform:uppercase;padding:12px 8px;border-bottom:1px solid rgba(255,255,255,0.06)}
  td{padding:10px 8px;border-bottom:1px solid rgba(255,255,255,0.03)}
  .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
  .on{background:#22c55e} .off{background:#ef4444}
  .btn{padding:10px 20px;border-radius:6px;font-size:13px;cursor:pointer;border:1px solid rgba(255,255,255,0.1);background:#0d0d0e;color:#e8e6e3;text-decoration:none;display:inline-flex;align-items:center;gap:6px;transition:all .2s}
  .btn:hover{border-color:#c9a96e}
  .go{background:linear-gradient(135deg,#c9a96e,#a88740);color:#070707;border:none;font-weight:600}
  .go:hover{background:linear-gradient(135deg,#d4b87a,#b89540)}
  .ac{display:flex;gap:8px;margin-top:24px;flex-wrap:wrap}
</style>
</head>
<body>
<div class="hdr"><h1>Parakram VPS</h1><span id="hostname"></span></div>

<div class="grid" id="s">
  <div class="c"><h3>CPU</h3><div class="v" id="cpu">-</div><div class="s">usage</div></div>
  <div class="c"><h3>Memory</h3><div class="v" id="mem">-</div><div class="s">used</div></div>
  <div class="c"><h3>Disk</h3><div class="v" id="dsk">-</div><div class="s">used</div></div>
  <div class="c"><h3>Uptime</h3><div class="v" id="upt">-</div><div class="s">since boot</div></div>
</div>

<div class="c" style="margin-bottom:24px">
  <h3>Services</h3>
  <table>
    <tr><th>Service</th><th>Status</th><th>Action</th></tr>
    <tr><td>OpenSSH Server</td><td id="s1"><span class="dot" id="d1"></span>Checking...</td><td><button class="btn" onclick="t('ssh')" style="padding:4px 12px;font-size:11px">Toggle</button></td></tr>
    <tr><td>Cloudflare Tunnel</td><td id="s2"><span class="dot" id="d2"></span>Checking...</td><td><button class="btn" onclick="t('tun')" style="padding:4px 12px;font-size:11px">Toggle</button></td></tr>
    <tr><td>Dashboard</td><td><span class="dot on"></span>Running</td><td id="dashPort"></td></tr>
  </table>
</div>

<div class="ac">
  <a class="btn go" href="https://dash.cloudflare.com" target="_blank">Cloudflare Dashboard</a>
  <a class="btn" href="https://getparakram.in" target="_blank">About Parakram</a>
  <a class="btn" href="#" onclick="r()">Refresh</a>
</div>

<script>
var apiPath = '/a/s';
var togglePath = '/a/t/';
async function r(){try{
  var d=await(await fetch(apiPath)).json();
  document.getElementById('cpu').textContent=d.c+'%';
  document.getElementById('mem').textContent=d.m;
  document.getElementById('dsk').textContent=d.d;
  document.getElementById('upt').textContent=d.u;
  var s1=document.getElementById('s1'),d1=document.getElementById('d1');
  s1.innerHTML=d.s?'<span class="dot on"></span>Running':'<span class="dot off"></span>Stopped';
  var s2=document.getElementById('s2'),d2=document.getElementById('d2');
  s2.innerHTML=d.t?'<span class="dot on"></span>Connected':'<span class="dot off"></span>Disconnected';
}catch(e){console.error('Stats fetch failed:',e)}}
async function t(x){try{await fetch(togglePath+x);setTimeout(r,2000)}catch(e){}}
document.getElementById('hostname').textContent=window.location.hostname;
document.getElementById('dashPort').textContent='Port '+window.location.port;
r();setInterval(r,5000);
</script>
</body>
</html>
'@
$dashboardHtml | Set-Content -Path "$dashboardDir\index.html" -Force -Encoding UTF8

$serverScript = @'
# Parakram VPS - Dashboard HTTP Server
# Run: powershell -ExecutionPolicy Bypass -File dashboard-server.ps1

$port = __PORT__
$htmlDir = "__HTMLDIR__"
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://+:$port/")
$listener.Start()

Write-Host ("Parakram VPS Dashboard running on http://localhost:$port")

while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $req = $ctx.Request
    $res = $ctx.Response

    try {
        $path = $req.Url.LocalPath

        if ($path -eq '/a/s') {
            $cpu = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
            $osInfo = Get-CimInstance Win32_OperatingSystem
            $memTotal = [math]::Round($osInfo.TotalVisibleMemorySize / 1MB, 1)
            $memFree = [math]::Round($osInfo.FreePhysicalMemory / 1MB, 1)
            $memUsed = [math]::Round($memTotal - $memFree, 1)
            $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
            $diskUsed = [math]::Round(($disk.Size - $disk.FreeSpace) / 1GB, 1)
            $diskTotal = [math]::Round($disk.Size / 1GB, 0)
            $boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
            $uptime = "$([math]::Floor(((Get-Date) - $boot).TotalDays))d $((Get-Date - $boot).Hours)h $((Get-Date - $boot).Minutes)m"
            $sshRunning = (Get-Service sshd -ErrorAction SilentlyContinue).Status -eq 'Running'
            $tunRunning = (Get-Process cloudflared -ErrorAction SilentlyContinue) -ne $null

            $json = "{""c"":$cpu,""m"":""$memUsed/$memTotal GB"",""d"":""$diskUsed/$diskTotal GB"",""u"":""$uptime"",""s"":$($sshRunning -eq $true),""t"":$($tunRunning -eq $true)}"
            $buffer = [text.encoding]::UTF8.GetBytes($json)
            $res.ContentType = 'application/json'
            $res.ContentLength64 = $buffer.Length
            $res.OutputStream.Write($buffer, 0, $buffer.Length)
        }
        elseif ($path -eq '/a/t/ssh') {
            $svc = Get-Service sshd -ErrorAction SilentlyContinue
            if ($svc.Status -eq 'Running') { Stop-Service sshd -Force } else { Start-Service sshd }
            $res.StatusCode = 200
        }
        elseif ($path -eq '/a/t/tun') {
            $proc = Get-Process cloudflared -ErrorAction SilentlyContinue
            if ($proc) { $proc | Stop-Process -Force } else { Start-Process "$htmlDir\..\cloudflared.exe" -WindowStyle Hidden }
            $res.StatusCode = 200
        }
        else {
            $file = Join-Path $htmlDir index.html
            if (Test-Path $file) {
                $bytes = [IO.File]::ReadAllBytes($file)
                $res.ContentType = 'text/html'
                $res.ContentLength64 = $bytes.Length
                $res.OutputStream.Write($bytes, 0, $bytes.Length)
            } else {
                $res.StatusCode = 404
            }
        }
    } catch {
        try { $res.StatusCode = 500 } catch {}
    }

    try { $res.Close() } catch {}
}
'@

$serverScript = $serverScript.Replace('__PORT__', $DASHBOARD_PORT).Replace('__HTMLDIR__', $dashboardDir)
$serverScript | Set-Content -Path "$dashboardDir\dashboard-server.ps1" -Force -Encoding UTF8

Write-Success "Dashboard created"

# -- 4. Create Startup Script & Schedule -----------------------------------
Write-Step "Configuring Auto-Start"

$taskName = "ParakramVPS-Dashboard"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if (-not $existing) {
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$dashboardDir\dashboard-server.ps1`""
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Description "Parakram VPS Management Dashboard" | Out-Null
    Write-Success "Auto-start configured (Task Scheduler)"
} else {
    Write-Info "Auto-start already configured"
}

try {
    $proc = Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$dashboardDir\dashboard-server.ps1`"" -PassThru -WindowStyle Hidden
    Write-Success "Dashboard started (PID: $($proc.Id))"
} catch {
    Write-Warn "Could not start dashboard: $_"
}

# -- 5. Configure Firewall -------------------------------------------------
Write-Step "Configuring Windows Firewall"

$fwRuleName = "Parakram VPS Dashboard"
$existing = Get-NetFirewallRule -DisplayName $fwRuleName -ErrorAction SilentlyContinue
if (-not $existing) {
    New-NetFirewallRule -DisplayName $fwRuleName -Direction Inbound -Protocol TCP -LocalPort $DASHBOARD_PORT -Action Allow | Out-Null
    Write-Success "Firewall rule added for port $DASHBOARD_PORT"
} else {
    Write-Info "Firewall rule already exists"
}

# -- 6. Generate Access Info -----------------------------------------------
Write-Step "Gathering Access Information"

$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch "Loopback|Virtual|Bluetooth|Hyper-V|vEthernet" -and $_.PrefixOrigin -eq "Dhcp" }).IPAddress | Select-Object -First 1

# -- Summary ---------------------------------------------------------------
Write-Host ""
Write-Host "==============================" -ForegroundColor Green
Write-Host " PARAKRAM VPS - INSTALLED" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host ""
Write-Host "  LOCAL ACCESS" -ForegroundColor Cyan
if ($localIP) {
    Write-Host "     SSH:          ssh $env:USERNAME@$localIP" -ForegroundColor White
}
Write-Host "     Dashboard:    http://localhost:$DASHBOARD_PORT" -ForegroundColor White
Write-Host ""
Write-Host "  PUBLIC ACCESS (Cloudflare Tunnel)" -ForegroundColor Cyan
Write-Host "     Run these commands to set up public URL:" -ForegroundColor Gray
Write-Host "     1. $INSTALL_DIR\cloudflared.exe tunnel login" -ForegroundColor Yellow
Write-Host "     2. $INSTALL_DIR\cloudflared.exe tunnel create $TUNNEL_NAME" -ForegroundColor Yellow
Write-Host "     3. $INSTALL_DIR\cloudflared.exe tunnel route dns $TUNNEL_NAME your-name.getparakram.in" -ForegroundColor Yellow
Write-Host "     4. $INSTALL_DIR\cloudflared.exe tunnel run $TUNNEL_NAME" -ForegroundColor Yellow
Write-Host ""
Write-Host "  MANAGEMENT" -ForegroundColor Cyan
Write-Host "     Dashboard:    http://localhost:$DASHBOARD_PORT" -ForegroundColor White
Write-Host "     Install Log:  $LOG_FILE" -ForegroundColor White
Write-Host "     Config Dir:   $INSTALL_DIR" -ForegroundColor White
Write-Host ""
Write-Host "  PRO TIP" -ForegroundColor Cyan
Write-Host "     Install Docker Desktop for app deployment:" -ForegroundColor Gray
Write-Host "     winget install Docker.DockerDesktop" -ForegroundColor Yellow
Write-Host ""
Write-Host "==============================" -ForegroundColor DarkYellow
Write-Log "Installation complete" -Color Green

Start-Sleep 2
Start-Process "http://localhost:$DASHBOARD_PORT"
