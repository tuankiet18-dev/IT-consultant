# Optional: builds an English voice-over from narration.txt with the voices that come with Windows (offline).
# Use it if nobody on the team wants to read the narration aloud. A human voice sounds better; this is a fallback.
#
# Output: deliverables\video-kit\out\audio\s1.wav, s2.wav, s3a.wav, s3b.wav, ... (one file per beat, in scene order)
# Run:    powershell -ExecutionPolicy Bypass -File deliverables\video-kit\scripts\make-voiceover.ps1
# Voice:  add -Voice "Microsoft David Desktop" to choose a voice; -Rate -1 to speak slower (range -10 to 10)
param([string]$Voice = "", [int]$Rate = 0)

$ErrorActionPreference = "Stop"
$kit = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $kit "out\audio"
New-Item -ItemType Directory -Force $outDir | Out-Null
Get-ChildItem $outDir -Filter "*.wav" | Remove-Item -Force

Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$english = $synth.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Culture.Name -like "en-*" }
if (-not $english) { Write-Host "No English voice is installed. Add one in Windows Settings > Time & language > Speech." -ForegroundColor Red; exit 1 }
$chosen = $null
if ($Voice) { $chosen = $english | Where-Object { $_.VoiceInfo.Name -eq $Voice } | Select-Object -First 1 }
if (-not $chosen) { $chosen = $english | Where-Object { $_.VoiceInfo.Name -match "Zira|Aria|Jenny|David" } | Select-Object -First 1 }
if (-not $chosen) { $chosen = $english | Select-Object -First 1 }
$synth.SelectVoice($chosen.VoiceInfo.Name)
$synth.Rate = $Rate
Write-Host ("Voice: " + $chosen.VoiceInfo.Name)

# parse narration.txt: "[Scene N ...]" headers, paragraphs separated by blank lines
$lines = Get-Content (Join-Path $kit "narration.txt") -Encoding UTF8
$scenes = [ordered]@{}
$cur = $null
$buf = New-Object System.Collections.ArrayList
function Flush-Paragraph { if ($script:buf.Count -gt 0 -and $script:cur) { $scenes[$script:cur].Add(($script:buf -join " ")) | Out-Null; $script:buf.Clear() } }
foreach ($l in $lines) {
    if ($l -match '^\[Scene (\d+) ') { Flush-Paragraph; $cur = $Matches[1]; $scenes[$cur] = New-Object System.Collections.ArrayList; continue }
    if (-not $cur) { continue }
    if ($l.Trim() -eq "") { Flush-Paragraph } else { [void]$buf.Add($l.Trim()) }
}
Flush-Paragraph

$total = 0.0
foreach ($n in $scenes.Keys) {
    $paras = $scenes[$n]
    for ($k = 0; $k -lt $paras.Count; $k++) {
        $suffix = if ($paras.Count -gt 1) { [string][char](97 + $k) } else { "" }
        $file = Join-Path $outDir ("s" + $n + $suffix + ".wav")
        $synth.SetOutputToWaveFile($file)
        $synth.Speak($paras[$k])
        $synth.SetOutputToNull()
        $bytes = (Get-Item $file).Length
        $secs = [math]::Round(($bytes - 44) / 44100.0, 1)   # 22.05 kHz, 16-bit, mono
        $total += $secs
        Write-Host ("s" + $n + $suffix + ".wav  " + $secs + " s")
    }
}
$synth.Dispose()
Write-Host ("Total speech: " + [math]::Round($total, 1) + " s. Files are in " + $outDir)
