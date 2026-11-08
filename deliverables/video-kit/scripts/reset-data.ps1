# Stops the app on port 8000 and moves the local database aside (a backup is kept), so the next start is clean.
# Use it before every full take, or to stop the app after recording.
$ErrorActionPreference = "Stop"
$kit = Split-Path -Parent $PSScriptRoot
$repo = (Resolve-Path (Join-Path $kit "..\..")).Path
$var = Join-Path $repo "mvp\var"

Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Milliseconds 800

if (Test-Path $var) {
    $backup = "$var`_backup_" + (Get-Date -Format "yyyyMMdd-HHmmss")
    Move-Item $var $backup
    Write-Host "Old data moved to $backup (delete it when you no longer need it)."
} else {
    Write-Host "No local data found: already clean."
}
Write-Host "App stopped and data cleared."
