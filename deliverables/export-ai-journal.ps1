# Exports docs\round2\AI-Journal-DRAFT.docx to deliverables\AI Journal.pdf using Microsoft Word.
# Run it only after every yellow [..] cell in the draft has been filled in.
#   powershell -ExecutionPolicy Bypass -File deliverables\export-ai-journal.ps1
# (No Word? Open the .docx, File > Save As > PDF, and name it "AI Journal.pdf".)
$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$src = Join-Path $repo "docs\round2\AI-Journal-DRAFT.docx"
$out = Join-Path $PSScriptRoot "AI Journal.pdf"

if (-not (Test-Path $src)) { Write-Host "Draft not found: $src" -ForegroundColor Red; exit 1 }

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($src, $false, $true)    # read-only: the draft is not modified
    $doc.SaveAs2($out, 17)                               # 17 = PDF
    $pages = $doc.ComputeStatistics(2)
    $doc.Close($false)
    Write-Host "Wrote $out ($pages pages)." -ForegroundColor Green
} finally {
    try { $word.Quit() } catch { }
}
Write-Host "Now run:  python deliverables\check-submission.py"
