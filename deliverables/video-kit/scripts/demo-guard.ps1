# Scene 5: the "AI is blocked" demo, in a clean terminal. Needs no network and no key.
# Open a NEW PowerShell window, enlarge the font (Ctrl + mouse wheel), then run this file.
$ErrorActionPreference = "Stop"
$kit = Split-Path -Parent $PSScriptRoot
$repo = (Resolve-Path (Join-Path $kit "..\..")).Path
$mvp = Join-Path $repo "mvp"
$py = Join-Path $mvp ".venv\Scripts\python.exe"

Remove-Item Env:GROQ_API_KEY -ErrorAction SilentlyContinue
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONWARNINGS = "ignore"
Set-Location $mvp
Clear-Host
$Host.UI.RawUI.WindowTitle = "Nordic Flow: AI guard demo"
Write-Host "PS nordic-flow> python -m nordic_flow demo-guard" -ForegroundColor Cyan
Write-Host ""
$ErrorActionPreference = "Continue"
& $py -m nordic_flow demo-guard
Write-Host ""
Write-Host "ACCEPTED = every figure is in the calculated facts. REJECTED = an invented figure; the standard summary is used instead." -ForegroundColor DarkGray
