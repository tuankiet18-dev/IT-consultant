# Speaks every subtitle cue with a Windows voice (offline) -> cue_001.wav, cue_002.wav, ...
# Used by build-video.py. Usage: tts-cues.ps1 -Json cues.json -OutDir out\tts [-Voice "Microsoft Zira Desktop"] [-Rate 0]
param([Parameter(Mandatory)][string]$Json, [Parameter(Mandatory)][string]$OutDir, [string]$Voice = "Microsoft Zira Desktop", [int]$Rate = 0)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech
New-Item -ItemType Directory -Force $OutDir | Out-Null
Get-ChildItem $OutDir -Filter "cue_*.wav" | Remove-Item -Force
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try { $synth.SelectVoice($Voice) } catch { Write-Host "Voice '$Voice' not found, using the default." }
$synth.Rate = $Rate
$texts = Get-Content $Json -Raw -Encoding UTF8 | ConvertFrom-Json
$n = 0
foreach ($t in $texts) {
    $n++
    $synth.SetOutputToWaveFile((Join-Path $OutDir ("cue_{0:000}.wav" -f $n)))
    $synth.Speak([string]$t)
    $synth.SetOutputToNull()
}
$synth.Dispose()
Write-Host "$n cues spoken with $($synth.Voice.Name)"
