# Starts a clean Nordic Flow instance for recording MVP.mp4.
#   - backs up and clears the local database so plans are numbered from 1
#   - runs the pre-flight check (the numbers quoted in the narration)
#   - optionally asks for a Groq key for the AI scene (typed hidden, never saved, never printed)
#   - starts the app on http://localhost:8000 and opens it in the browser
#
# Run from anywhere:   powershell -ExecutionPolicy Bypass -File deliverables\video-kit\scripts\start-recording.ps1
# Without the AI scene: add -NoAI        Skip the check: add -NoPreflight        Do not open the browser: add -NoBrowser
param([switch]$NoAI, [switch]$NoPreflight, [switch]$NoBrowser)

$ErrorActionPreference = "Stop"
$kit = Split-Path -Parent $PSScriptRoot
$repo = (Resolve-Path (Join-Path $kit "..\..")).Path
$mvp = Join-Path $repo "mvp"
$py = Join-Path $mvp ".venv\Scripts\python.exe"

if (-not (Test-Path $py)) {
    Write-Host "Python environment not found at $py" -ForegroundColor Red
    Write-Host "Create it once:  cd mvp ; python -m venv .venv ; .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
    exit 1
}

# 1. clean start
& (Join-Path $PSScriptRoot "reset-data.ps1")

# 2. AI key for this session only
Remove-Item Env:GROQ_API_KEY -ErrorAction SilentlyContinue
if (-not $NoAI) {
    $secure = Read-Host "Groq API key for the AI scene (press Enter to record without AI)" -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    if ($plain) { $env:GROQ_API_KEY = $plain }
    $plain = $null
}

# 3. pre-flight
if (-not $NoPreflight) {
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONWARNINGS = "ignore"
    $ErrorActionPreference = "Continue"
    & $py (Join-Path $PSScriptRoot "preflight.py")
    $code = $LASTEXITCODE
    $ErrorActionPreference = "Stop"
    Remove-Item Env:PYTHONWARNINGS -ErrorAction SilentlyContinue
    if ($code -ne 0) {
        Write-Host "Pre-flight failed. Fix the FAIL lines above before recording." -ForegroundColor Red
        exit 1
    }
}

# 4. start the app in the background (no window on screen); the log goes to a file
$log = Join-Path $env:TEMP "nordic-flow-server.log"
Start-Process -FilePath $py -ArgumentList "-m", "uvicorn", "api.main:app", "--port", "8000" -WorkingDirectory $mvp -WindowStyle Hidden -RedirectStandardOutput $log -RedirectStandardError ($log + ".err") | Out-Null

# wait until the port accepts connections (up to 60 s)
$ok = $false
for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $c = New-Object Net.Sockets.TcpClient
        $c.Connect("127.0.0.1", 8000)
        $c.Close()
        $ok = $true
        break
    } catch { }
}
if (-not $ok) { Write-Host "The app did not start. Read the log: $log.err" -ForegroundColor Red; exit 1 }
Start-Sleep -Seconds 1

$cfg = $null
try { $cfg = Invoke-RestMethod "http://127.0.0.1:8000/api/config" -TimeoutSec 10 } catch { }
if (-not $NoBrowser) { Start-Process "http://localhost:8000" }

Write-Host ""
Write-Host "Nordic Flow is running at http://localhost:8000" -ForegroundColor Green
Write-Host ("AI assistant: " + $(if ($cfg -and $cfg.llm_enabled) { "ON (" + $cfg.llm_model + ")" } else { "OFF (the scene will show the standard summary)" }))
Write-Host ""
Write-Host "Files for the scenes:  $kit\data"
Write-Host "  nordic-flow-pilot-sample.zip   scene 3 (valid upload)"
Write-Host "  05_invalid_warehouse_cycle.zip scene 3 (data error)"
Write-Host "  baseline-unusable.zip          optional bonus scene"
Write-Host "Teleprompter:  $kit\teleprompter.html"
Write-Host "Terminal scene (open a NEW terminal, not this one):  $PSScriptRoot\demo-guard.ps1"
Write-Host ""
Write-Host "Close THIS window before recording so the screen shows nothing sensitive."
Write-Host "To stop the app later:  $PSScriptRoot\reset-data.ps1"
