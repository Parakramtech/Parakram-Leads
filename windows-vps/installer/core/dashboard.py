"""
PARAKRAM VPS — ENHANCED DASHBOARD GENERATOR
=============================================
Generates the management dashboard HTML with:
  - Resource history graphs (CSS sparklines, last 60 data points)
  - Container management panel (start/stop/restart Docker services)
  - System logs viewer with filtering
  - Update notification banner
  - Heartbeat connection indicator
  - Network throughput display
  - Quick actions panel (restart all, export diagnostics, open tunnel)

The generated HTML is a single self-contained file with no external dependencies.
All data fetching uses the existing PowerShell HttpListener API endpoints.
"""

DASHBOARD_VERSION = "2.1.0"


def generate_dashboard_html() -> str:
    """Generate the enhanced dashboard HTML."""
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Parakram VPS — Mission Control</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#070708;--surface:#0d0d0e;--surface2:#141416;--border:rgba(255,255,255,0.06);--gold:#c9a96e;--gold-dim:#a88740;--green:#22c55e;--red:#ef4444;--yellow:#eab308;--text:#e8e6e3;--text2:#8a8a8a;--text3:#5a5a5a;--mono:'Cascadia Code','Consolas',monospace;--sans:'Segoe UI',system-ui,sans-serif}
html,body{height:100%;overflow:hidden}
body{background:var(--bg);color:var(--text);font-family:var(--sans);display:flex;flex-direction:column}

/* Header */
.hdr{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;border-bottom:1px solid var(--border);flex-shrink:0}
.hdr-left{display:flex;align-items:center;gap:12px}
.hdr h1{font-size:16px;font-weight:600;color:var(--gold);letter-spacing:0.05em}
.hdr h1 small{font-size:10px;color:var(--text3);font-weight:400;margin-left:6px}
.hdr-right{display:flex;align-items:center;gap:12px}
.hdr-status{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--text3);font-family:var(--mono)}
.pulse{width:8px;height:8px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
.pulse.off{background:var(--red);animation:none}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}

/* Update Banner */
.update-banner{display:none;background:linear-gradient(90deg,#1a1500,#0d0d0e);border-bottom:1px solid var(--gold);padding:8px 24px;font-size:12px;color:var(--gold);flex-shrink:0;align-items:center;gap:8px}
.update-banner.show{display:flex}
.update-banner a{color:var(--gold);font-weight:600;text-decoration:underline;cursor:pointer}

/* Main Content */
.main{flex:1;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto 1fr auto;gap:12px;padding:16px 24px;overflow:hidden}

/* Metric Cards */
.metrics{grid-column:1/-1;display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.mc{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px 16px;transition:border-color .3s}
.mc:hover{border-color:rgba(201,169,110,0.2)}
.mc h3{font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px}
.mc .val{font-size:22px;font-weight:700;font-variant-numeric:tabular-nums}
.mc .sub{font-size:11px;color:var(--text3);margin-top:2px}
.mc .bar{height:3px;background:#1a1a1c;border-radius:2px;margin-top:6px;overflow:hidden}
.mc .bar-fill{height:100%;border-radius:2px;transition:width .5s ease}
.mc .sparkline{display:flex;align-items:flex-end;gap:1px;height:24px;margin-top:6px}
.mc .sparkline .sp{background:var(--gold);opacity:0.4;border-radius:1px;min-width:2px;flex:1;transition:height .3s}
.mc .sparkline .sp:last-child{opacity:1}

/* Panels */
.panel{background:var(--surface);border:1px solid var(--border);border-radius:8px;overflow:hidden;display:flex;flex-direction:column}
.panel-hdr{padding:12px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.panel-hdr h3{font-size:11px;color:var(--text3);text-transform:uppercase;letter-spacing:0.1em}
.panel-body{flex:1;overflow-y:auto;padding:8px 0}

/* Services Table */
.svc-table{width:100%;border-collapse:collapse;font-size:12px}
.svc-table th{text-align:left;font-size:10px;color:var(--text3);text-transform:uppercase;padding:8px 16px;letter-spacing:0.05em}
.svc-table td{padding:8px 16px;border-top:1px solid var(--border)}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:6px}
.dot.on{background:var(--green);box-shadow:0 0 6px rgba(34,197,94,0.4)}
.dot.off{background:var(--red);box-shadow:0 0 6px rgba(239,68,68,0.4)}
.dot.warn{background:var(--yellow);box-shadow:0 0 6px rgba(234,179,8,0.4)}
.svc-btn{padding:3px 10px;border-radius:4px;font-size:10px;cursor:pointer;border:1px solid var(--border);background:var(--surface2);color:var(--text2);font-family:var(--sans);transition:all .2s}
.svc-btn:hover{border-color:var(--gold);color:var(--text)}
.svc-btn.danger:hover{border-color:var(--red);color:var(--red)}

/* Logs Panel */
.log-controls{display:flex;gap:6px;padding:0 16px 8px;flex-shrink:0}
.log-filter{padding:3px 8px;border-radius:3px;font-size:10px;cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--text3);font-family:var(--sans)}
.log-filter.active{border-color:var(--gold);color:var(--gold)}
.log-content{flex:1;overflow-y:auto;padding:0 16px;font-family:var(--mono);font-size:11px;line-height:1.7;color:var(--text3)}
.log-content .error{color:var(--red)}
.log-content .warn{color:var(--yellow)}
.log-content .ok{color:var(--green)}
.log-content .ts{color:var(--text3);opacity:0.6}

/* Containers Panel */
.container-row{display:flex;align-items:center;justify-content:space-between;padding:8px 16px;border-top:1px solid var(--border)}
.container-row:first-child{border-top:none}
.container-info{display:flex;align-items:center;gap:8px}
.container-name{font-size:12px;color:var(--text)}
.container-image{font-size:10px;color:var(--text3);font-family:var(--mono)}
.container-actions{display:flex;gap:4px}

/* Footer Actions */
.footer{grid-column:1/-1;display:flex;gap:8px;flex-shrink:0;padding-top:4px}
.btn{padding:8px 16px;border-radius:6px;font-size:12px;cursor:pointer;border:1px solid var(--border);background:var(--surface);color:var(--text);text-decoration:none;display:inline-flex;align-items:center;gap:5px;transition:all .2s;font-family:inherit}
.btn:hover{border-color:var(--gold);background:var(--surface2)}
.btn.primary{background:linear-gradient(135deg,var(--gold),var(--gold-dim));color:#070707;border:none;font-weight:600}
.btn.primary:hover{opacity:0.9}

/* Alert */
.alert{position:fixed;top:60px;right:24px;padding:10px 16px;border-radius:6px;font-size:12px;display:none;z-index:100;box-shadow:0 4px 12px rgba(0,0,0,0.4);animation:slideIn .3s ease}
@keyframes slideIn{from{transform:translateX(20px);opacity:0}to{transform:translateX(0);opacity:1}}

/* Responsive */
@media(max-width:900px){.main{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}}
</style></head>
<body>
<div id="update-banner" class="update-banner">
  <span>&#x2728; Update available: <strong id="update-version">—</strong></span>
  <a onclick="window.open('https://getparakram.in/store','_blank')">Download</a>
</div>
<div class="hdr">
  <div class="hdr-left">
    <h1>PARAKRAM VPS <small>Mission Control v2.1</small></h1>
  </div>
  <div class="hdr-right">
    <div class="hdr-status"><span id="hb-dot" class="pulse"></span><span id="hb-text">Connected</span></div>
    <span style="color:var(--text3);font-size:11px;font-family:var(--mono)" id="hostname">—</span>
  </div>
</div>

<div class="main">
  <!-- Metrics Row -->
  <div class="metrics">
    <div class="mc"><h3>CPU</h3><div class="val" id="cpu">—</div><div class="sub">utilization</div><div class="bar"><div class="bar-fill" id="cpu-bar" style="width:0%"></div></div><div class="sparkline" id="cpu-spark"></div></div>
    <div class="mc"><h3>Memory</h3><div class="val" id="mem">—</div><div class="sub" id="mem-sub">used / total</div><div class="bar"><div class="bar-fill" id="mem-bar" style="width:0%"></div></div><div class="sparkline" id="mem-spark"></div></div>
    <div class="mc"><h3>Disk</h3><div class="val" id="dsk">—</div><div class="sub" id="dsk-sub">used / total</div><div class="bar"><div class="bar-fill" id="dsk-bar" style="width:0%"></div></div></div>
    <div class="mc"><h3>Uptime</h3><div class="val" id="upt">—</div><div class="sub">since boot</div></div>
    <div class="mc"><h3>Network</h3><div class="val" id="net">—</div><div class="sub" id="net-sub">tunnel status</div></div>
  </div>

  <!-- Services Panel -->
  <div class="panel">
    <div class="panel-hdr"><h3>Services</h3><button class="svc-btn" onclick="restartAll()">Restart All</button></div>
    <div class="panel-body">
      <table class="svc-table">
        <tr><th>Service</th><th>Status</th><th>Action</th></tr>
        <tr><td>OpenSSH Server</td><td id="s-ssh"><span class="dot off"></span>Scanning...</td><td><button class="svc-btn" onclick="toggle('ssh')">Toggle</button></td></tr>
        <tr><td>Cloudflare Tunnel</td><td id="s-tun"><span class="dot off"></span>Scanning...</td><td><button class="svc-btn" onclick="toggle('tun')">Toggle</button></td></tr>
        <tr><td>Dashboard Server</td><td><span class="dot on"></span>Active</td><td>Port <span id="port-val">9876</span></td></tr>
        <tr><td>Leads Backend</td><td id="s-leads"><span class="dot off"></span>Scanning...</td><td><button class="svc-btn" onclick="toggle('leads')">Toggle</button></td></tr>
      </table>
    </div>
  </div>

  <!-- Containers Panel -->
  <div class="panel">
    <div class="panel-hdr"><h3>Containers</h3><button class="svc-btn" onclick="refreshContainers()">Refresh</button></div>
    <div class="panel-body" id="containers-body">
      <div style="padding:16px;color:var(--text3);font-size:12px;text-align:center">Loading container status...</div>
    </div>
  </div>

  <!-- Logs Panel -->
  <div class="panel" style="grid-column:1/-1">
    <div class="panel-hdr">
      <h3>System Events</h3>
      <div class="log-controls" style="padding:0">
        <button class="log-filter active" data-level="all" onclick="filterLogs('all',this)">All</button>
        <button class="log-filter" data-level="error" onclick="filterLogs('error',this)">Errors</button>
        <button class="log-filter" data-level="warn" onclick="filterLogs('warn',this)">Warnings</button>
        <button class="log-filter" data-level="ok" onclick="filterLogs('ok',this)">Info</button>
      </div>
    </div>
    <div class="log-content" id="log-content">
      <div class="ok"><span class="ts">[--:--:--]</span> Waiting for telemetry...</div>
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <a class="btn primary" href="https://dash.cloudflare.com" target="_blank" rel="noopener">&#x2601; Cloudflare</a>
    <button class="btn" onclick="exportDiagnostics()">&#x1F4CB; Export Diagnostics</button>
    <a class="btn" href="https://leads.getparakram.in" target="_blank" rel="noopener">&#x1F4CA; Leads Dashboard</a>
    <a class="btn" href="https://getparakram.in" target="_blank" rel="noopener">&#x2139; About</a>
    <button class="btn" onclick="location.reload()">&#x27F3; Refresh</button>
  </div>
</div>

<div id="alert" class="alert"></div>

<script>
// ── State ─────────────────────────────────────────────────────────────
var history={cpu:[],mem:[]};
var MAX_HISTORY=60;
var logEntries=[];
var currentFilter='all';
var pollFailCount=0;

// ── Sparkline Renderer ────────────────────────────────────────────────
function renderSparkline(containerId,data){
  var el=document.getElementById(containerId);
  if(!el)return;
  var max=Math.max.apply(null,data.concat([1]));
  el.innerHTML='';
  for(var i=0;i<data.length;i++){
    var d=document.createElement('div');
    d.className='sp';
    d.style.height=Math.max(2,data[i]/max*100)+'%';
    el.appendChild(d);
  }
}

// ── Bar Color ─────────────────────────────────────────────────────────
function barColor(p){
  if(p<50)return 'linear-gradient(90deg,#22c55e,#16a34a)';
  if(p<80)return 'linear-gradient(90deg,#eab308,#ca8a04)';
  return 'linear-gradient(90deg,#ef4444,#dc2626)';
}

// ── Log System ────────────────────────────────────────────────────────
function addLog(msg,level){
  level=level||'ok';
  var ts=new Date().toLocaleTimeString();
  logEntries.unshift({ts:ts,msg:msg,level:level});
  if(logEntries.length>200)logEntries.pop();
  renderLogs();
}

function renderLogs(){
  var el=document.getElementById('log-content');
  var html='';
  for(var i=0;i<Math.min(logEntries.length,100);i++){
    var e=logEntries[i];
    if(currentFilter!=='all'&&e.level!==currentFilter)continue;
    html+='<div class="'+e.level+'"><span class="ts">['+e.ts+']</span> '+e.msg+'</div>';
  }
  el.innerHTML=html||'<div style="color:var(--text3)">No entries match filter.</div>';
}

function filterLogs(level,btn){
  currentFilter=level;
  document.querySelectorAll('.log-filter').forEach(function(b){b.classList.remove('active')});
  btn.classList.add('active');
  renderLogs();
}

// ── Alert System ──────────────────────────────────────────────────────
function showAlert(msg,type){
  var el=document.getElementById('alert');
  el.textContent=msg;
  el.style.display='block';
  el.style.border='1px solid '+(type==='error'?'var(--red)':type==='warn'?'var(--yellow)':'var(--green)');
  el.style.background=type==='error'?'#1a0a0a':type==='warn'?'#1a1a0a':'#0a1a0a';
  el.style.color=type==='error'?'var(--red)':type==='warn'?'var(--yellow)':'var(--green)';
  setTimeout(function(){el.style.display='none'},6000);
}

// ── Main Poll ─────────────────────────────────────────────────────────
async function poll(){
  try{
    var r=await fetch('/a/s');
    if(!r.ok)throw new Error('HTTP '+r.status);
    var d=await r.json();
    pollFailCount=0;
    document.getElementById('hb-dot').className='pulse';
    document.getElementById('hb-text').textContent='Connected';

    // CPU
    var cpu=parseFloat(d.c)||0;
    history.cpu.push(cpu);
    if(history.cpu.length>MAX_HISTORY)history.cpu.shift();
    document.getElementById('cpu').textContent=cpu.toFixed(0)+'%';
    document.getElementById('cpu-bar').style.width=Math.min(cpu,100)+'%';
    document.getElementById('cpu-bar').style.background=barColor(cpu);
    renderSparkline('cpu-spark',history.cpu);

    // Memory
    var memMatch=d.m.match(/([\d.]+)/),memUsed=parseFloat(memMatch?memMatch[1]:0);
    var memTotalMatch=d.m.match(/\/\s*([\d.]+)/),memTotal=parseFloat(memTotalMatch?memTotalMatch[1]:1);
    var memPct=memTotal>0?Math.min((memUsed/memTotal)*100,100):0;
    history.mem.push(memPct);
    if(history.mem.length>MAX_HISTORY)history.mem.shift();
    document.getElementById('mem').textContent=memPct.toFixed(0)+'%';
    document.getElementById('mem-sub').textContent=memUsed.toFixed(1)+' / '+memTotal.toFixed(1)+' GB';
    document.getElementById('mem-bar').style.width=memPct+'%';
    document.getElementById('mem-bar').style.background=barColor(memPct);
    renderSparkline('mem-spark',history.mem);

    // Disk
    var dskMatch=d.d.match(/([\d.]+)/),dskUsed=parseFloat(dskMatch?dskMatch[1]:0);
    var dskTotalMatch=d.d.match(/\/\s*([\d.]+)/),dskTotal=parseFloat(dskTotalMatch?dskTotalMatch[1]:1);
    var dskPct=dskTotal>0?Math.min((dskUsed/dskTotal)*100,100):0;
    document.getElementById('dsk').textContent=dskPct.toFixed(0)+'%';
    document.getElementById('dsk-sub').textContent=dskUsed.toFixed(1)+' / '+dskTotal.toFixed(0)+' GB';
    document.getElementById('dsk-bar').style.width=dskPct+'%';
    document.getElementById('dsk-bar').style.background=barColor(dskPct);

    // Uptime
    document.getElementById('upt').textContent=d.u||'—';

    // Services
    var ssh=d.s===true||d.s==='true';
    var tun=d.t===true||d.t==='true';
    document.getElementById('s-ssh').innerHTML=ssh?'<span class="dot on"></span>Running':'<span class="dot off"></span>Stopped';
    document.getElementById('s-tun').innerHTML=tun?'<span class="dot on"></span>Connected':'<span class="dot off"></span>Disconnected';
    document.getElementById('port-val').textContent=d.p||'9876';

    // Network/Tunnel
    document.getElementById('net').textContent=tun?'Active':'Offline';
    document.getElementById('net-sub').textContent=tun?'tunnel connected':'tunnel disconnected';

    // Leads
    var leads=d.l||'unknown';
    var leadsEl=document.getElementById('s-leads');
    if(leads==='running')leadsEl.innerHTML='<span class="dot on"></span>Running';
    else if(leads==='starting')leadsEl.innerHTML='<span class="dot warn"></span>Starting...';
    else if(leads==='not_installed')leadsEl.innerHTML='<span class="dot off"></span>Not Installed';
    else leadsEl.innerHTML='<span class="dot off"></span>'+leads;

    // Alerts
    if(cpu>90)showAlert('High CPU: '+cpu.toFixed(0)+'%','warn');
    if(memPct>90)showAlert('High Memory: '+memPct.toFixed(0)+'%','warn');
    if(dskPct>90)showAlert('Low Disk Space: '+dskPct.toFixed(0)+'% used','warn');

  }catch(e){
    pollFailCount++;
    if(pollFailCount>=3){
      document.getElementById('hb-dot').className='pulse off';
      document.getElementById('hb-text').textContent='Disconnected';
    }
    addLog('Poll failed: '+e.message,'error');
  }
}

// ── Container Management ──────────────────────────────────────────────
async function refreshContainers(){
  var el=document.getElementById('containers-body');
  try{
    var r=await fetch('/a/containers');
    if(!r.ok){
      el.innerHTML='<div style="padding:16px;color:var(--text3);font-size:12px;text-align:center">Docker not available or no containers running.</div>';
      return;
    }
    var containers=await r.json();
    if(!containers||!containers.length){
      el.innerHTML='<div style="padding:16px;color:var(--text3);font-size:12px;text-align:center">No containers found.</div>';
      return;
    }
    var html='';
    for(var i=0;i<containers.length;i++){
      var c=containers[i];
      var dot=c.state==='running'?'on':c.state==='exited'?'off':'warn';
      html+='<div class="container-row">';
      html+='<div class="container-info"><span class="dot '+dot+'"></span>';
      html+='<span class="container-name">'+c.name+'</span>';
      html+='<span class="container-image">'+c.image+'</span></div>';
      html+='<div class="container-actions">';
      if(c.state==='running')html+='<button class="svc-btn danger" onclick="containerAction(\''+c.name+'\',\'stop\')">Stop</button>';
      else html+='<button class="svc-btn" onclick="containerAction(\''+c.name+'\',\'start\')">Start</button>';
      html+='<button class="svc-btn" onclick="containerAction(\''+c.name+'\',\'restart\')">Restart</button>';
      html+='</div></div>';
    }
    el.innerHTML=html;
  }catch(e){
    el.innerHTML='<div style="padding:16px;color:var(--text3);font-size:12px;text-align:center">Failed to load containers.</div>';
  }
}

async function containerAction(name,action){
  try{
    await fetch('/a/container/'+name+'/'+action,{method:'POST'});
    addLog('Container '+name+': '+action,'ok');
    setTimeout(refreshContainers,2000);
  }catch(e){addLog('Container action failed: '+e.message,'error');}
}

// ── Service Toggle ────────────────────────────────────────────────────
async function toggle(svc){
  try{
    await fetch('/a/t/'+svc);
    addLog('Toggling: '+svc,'ok');
    setTimeout(poll,2000);
  }catch(e){addLog('Toggle failed: '+e.message,'error');}
}

async function restartAll(){
  addLog('Restarting all services...','warn');
  try{
    await fetch('/a/t/ssh');
    await fetch('/a/t/tun');
    await fetch('/a/t/leads');
    setTimeout(function(){
      toggle('ssh');toggle('tun');toggle('leads');
    },3000);
    addLog('All services restart initiated','ok');
  }catch(e){addLog('Restart failed: '+e.message,'error');}
}

// ── Export Diagnostics ────────────────────────────────────────────────
function exportDiagnostics(){
  var data={
    timestamp:new Date().toISOString(),
    hostname:document.getElementById('hostname').textContent,
    metrics_history:history,
    logs:logEntries.slice(0,50),
    user_agent:navigator.userAgent
  };
  var blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='parakram-vps-diagnostics-'+Date.now()+'.json';
  a.click();
  addLog('Diagnostics exported','ok');
}

// ── Check for Updates ─────────────────────────────────────────────────
async function checkUpdate(){
  try{
    var r=await fetch('/a/update-check');
    if(r.ok){
      var d=await r.json();
      if(d.available){
        document.getElementById('update-banner').classList.add('show');
        document.getElementById('update-version').textContent='v'+d.version;
        addLog('Update available: v'+d.version+(d.critical?' (CRITICAL)':''),'warn');
      }
    }
  }catch(e){}
}

// ── Init ──────────────────────────────────────────────────────────────
document.getElementById('hostname').textContent=window.location.hostname||'localhost';
addLog('Dashboard initialized','ok');
poll();
setInterval(poll,5000);
refreshContainers();
setInterval(refreshContainers,30000);
checkUpdate();
setInterval(checkUpdate,3600000);
</script>
</body>
</html>"""


def generate_server_script(port: int, html_dir: str, version: str = "2.1.0") -> str:
    """Generate the enhanced PowerShell dashboard server script."""
    return f"""# PARAKRAM VPS DASHBOARD SERVER v{version}
# Auto-generated by installer
# Endpoints: /a/s (stats), /a/t/* (toggle), /a/containers, /a/container/*/*, /a/update-check

param(
    [int]$Port = {port},
    [string]$HtmlDir = "{html_dir}",
    [int]$MaxRequests = 50000
)

$ErrorActionPreference = "Stop"
$hostName = [System.Net.Dns]::GetHostName()
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://+:$Port/")
$listener.Start()

$startTime = Get-Date
$startEntry = "[$($startTime.ToString('yyyy-MM-ddTHH:mm:sszzz'))] PARAKRAM VPS DASHBOARD STARTED on port $Port"
$startEntry | Out-File -FilePath "$env:USERPROFILE\\parakram-vps-dashboard.log" -Append -Encoding UTF8

$requestCount = 0
while ($listener.IsListening -and $requestCount -lt $MaxRequests) {{
    try {{
        $ctx = $listener.GetContext()
        $requestCount++
        $req = $ctx.Request
        $res = $ctx.Response

        try {{
            $path = $req.Url.LocalPath.TrimEnd('/')

            if ($path -eq '/a/s') {{
                # ── System Stats API ───────────────────────────────
                try {{
                    $cpu = (Get-CimInstance Win32_Processor -ErrorAction SilentlyContinue |
                        Measure-Object -Property LoadPercentage -Average).Average
                    if (-not $cpu) {{ $cpu = 0 }}
                }} catch {{ $cpu = 0 }}

                try {{
                    $osInfo = Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
                    $memTotal = [math]::Round($osInfo.TotalVisibleMemorySize / 1MB, 1)
                    $memFree = [math]::Round($osInfo.FreePhysicalMemory / 1MB, 1)
                    $memUsed = [math]::Round($memTotal - $memFree, 1)
                }} catch {{ $memUsed = 0; $memTotal = 1 }}

                try {{
                    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" -ErrorAction SilentlyContinue
                    $diskUsed = [math]::Round(($disk.Size - $disk.FreeSpace) / 1GB, 1)
                    $diskTotal = [math]::Round($disk.Size / 1GB, 0)
                }} catch {{ $diskUsed = 0; $diskTotal = 1 }}

                try {{
                    $boot = (Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue).LastBootUpTime
                    $uptimeSpan = (Get-Date) - $boot
                    $uptime = "$([math]::Floor($uptimeSpan.TotalDays))d $($uptimeSpan.Hours)h $($uptimeSpan.Minutes)m"
                }} catch {{ $uptime = "N/A" }}

                try {{ $sshRunning = (Get-Service sshd -ErrorAction SilentlyContinue).Status -eq 'Running' }}
                catch {{ $sshRunning = $false }}

                try {{ $tunRunning = (Get-Process cloudflared -ErrorAction SilentlyContinue) -ne $null }}
                catch {{ $tunRunning = $false }}

                try {{
                    $leadsDir = Join-Path (Split-Path $HtmlDir -Parent) "leads"
                    $leadsStatusFile = Join-Path $leadsDir "status.json"
                    if (Test-Path $leadsStatusFile) {{
                        $leadsJson = Get-Content $leadsStatusFile -Raw | ConvertFrom-Json
                        $leadsStatus = $leadsJson.status
                    }} else {{ $leadsStatus = "not_installed" }}
                }} catch {{ $leadsStatus = "unknown" }}

                $json = '{{"c":{0},"m":"{1}/{2} GB","d":"{3}/{4} GB","u":"{5}","s":{6},"t":{7},"p":{8},"l":"{9}"}}' -f
                    $cpu, $memUsed, $memTotal, $diskUsed, $diskTotal, $uptime,
                    ($sshRunning -eq $true).ToString().ToLower(),
                    ($tunRunning -eq $true).ToString().ToLower(),
                    $Port, $leadsStatus

                $buffer = [text.encoding]::UTF8.GetBytes($json)
                $res.ContentType = 'application/json'
                $res.OutputStream.Write($buffer, 0, $buffer.Length)

            }} elseif ($path -eq '/a/t/ssh') {{
                $svc = Get-Service sshd -ErrorAction SilentlyContinue
                if ($svc.Status -eq 'Running') {{ Stop-Service sshd -Force }}
                else {{ Start-Service sshd }}
                $res.StatusCode = 200

            }} elseif ($path -eq '/a/t/tun') {{
                $proc = Get-Process cloudflared -ErrorAction SilentlyContinue
                if ($proc) {{ $proc | Stop-Process -Force }}
                else {{
                    $cfExe = Join-Path (Split-Path $HtmlDir -Parent) "cloudflared.exe"
                    if (Test-Path $cfExe) {{ Start-Process -FilePath $cfExe -WindowStyle Hidden -ArgumentList "tunnel run" }}
                }}
                $res.StatusCode = 200

            }} elseif ($path -eq '/a/t/leads') {{
                try {{
                    $leadsDir = Join-Path (Split-Path $HtmlDir -Parent) "leads"
                    if (Test-Path "$leadsDir\\docker-compose.yml") {{
                        $status = & "docker" "compose" "-f" "$leadsDir\\docker-compose.yml" "ps" "-q" 2>&1
                        if ($LASTEXITCODE -eq 0 -and $status) {{
                            & "docker" "compose" "-f" "$leadsDir\\docker-compose.yml" "stop"
                        }} else {{
                            & "docker" "compose" "-f" "$leadsDir\\docker-compose.yml" "start"
                        }}
                    }}
                }} catch {{ }}
                $res.StatusCode = 200

            }} elseif ($path -eq '/a/containers') {{
                # ── List Docker Containers ─────────────────────────
                try {{
                    $containerJson = & "docker" "ps" "-a" "--format" "{{{{json .}}}}" 2>&1
                    if ($LASTEXITCODE -eq 0) {{
                        $containers = @()
                        foreach ($line in $containerJson) {{
                            if ($line -and $line.StartsWith('{{')) {{
                                $c = $line | ConvertFrom-Json
                                $containers += @{{
                                    name = $c.Names
                                    image = $c.Image
                                    state = $c.State
                                    status = $c.Status
                                }}
                            }}
                        }}
                        $jsonOut = $containers | ConvertTo-Json -Compress
                        if (-not $jsonOut) {{ $jsonOut = "[]" }}
                    }} else {{ $jsonOut = "[]" }}
                }} catch {{ $jsonOut = "[]" }}
                $buffer = [text.encoding]::UTF8.GetBytes($jsonOut)
                $res.ContentType = 'application/json'
                $res.OutputStream.Write($buffer, 0, $buffer.Length)

            }} elseif ($path -match '^/a/container/(.+)/(start|stop|restart)$') {{
                # ── Container Action ───────────────────────────────
                $containerName = $Matches[1]
                $action = $Matches[2]
                try {{
                    & "docker" $action $containerName 2>&1 | Out-Null
                    $res.StatusCode = 200
                }} catch {{ $res.StatusCode = 500 }}

            }} elseif ($path -eq '/a/update-check') {{
                # ── Update Check ───────────────────────────────────
                try {{
                    $updateFile = Join-Path (Split-Path $HtmlDir -Parent) ".update_staging" "update_meta.json"
                    if (Test-Path $updateFile) {{
                        $meta = Get-Content $updateFile -Raw | ConvertFrom-Json
                        $jsonOut = '{{"available":true,"version":"{0}","critical":{1}}}' -f $meta.version, ($meta.is_critical).ToString().ToLower()
                    }} else {{
                        $jsonOut = '{{"available":false}}'
                    }}
                }} catch {{ $jsonOut = '{{"available":false}}' }}
                $buffer = [text.encoding]::UTF8.GetBytes($jsonOut)
                $res.ContentType = 'application/json'
                $res.OutputStream.Write($buffer, 0, $buffer.Length)

            }} elseif ($path -eq '/a/h') {{
                $elapsed = ((Get-Date) - $startTime).TotalSeconds
                $jsonOut = '{{"status":"ok","uptime_seconds":{0},"requests":{1}}}' -f [int]$elapsed, $requestCount
                $buffer = [text.encoding]::UTF8.GetBytes($jsonOut)
                $res.ContentType = 'application/json'
                $res.OutputStream.Write($buffer, 0, $buffer.Length)

            }} else {{
                # ── Serve Static HTML ──────────────────────────────
                $file = Join-Path $HtmlDir "index.html"
                if (Test-Path $file) {{
                    $bytes = [IO.File]::ReadAllBytes($file)
                    $res.ContentType = 'text/html; charset=utf-8'
                    $res.OutputStream.Write($bytes, 0, $bytes.Length)
                }} else {{
                    $res.StatusCode = 404
                    $buffer = [text.encoding]::UTF8.GetBytes('404 - Reinstall Parakram VPS')
                    $res.OutputStream.Write($buffer, 0, $buffer.Length)
                }}
            }}
        }} catch {{
            $errorMsg = "[$(Get-Date)] ERROR on $path : $_"
            $errorMsg | Out-File -FilePath "$env:USERPROFILE\\parakram-vps-dashboard.log" -Append -Encoding UTF8
        }} finally {{
            try {{ $res.Close() }} catch {{ }}
        }}
    }} catch {{
        if (-not $listener.IsListening) {{ break }}
    }}
}}

$listener.Stop()
"[$(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz')] DASHBOARD STOPPED after $requestCount requests" |
    Out-File -FilePath "$env:USERPROFILE\\parakram-vps-dashboard.log" -Append -Encoding UTF8
"""
