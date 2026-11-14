#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$GameDirectory,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [switch]$PassTiming
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $GameDirectory).Path
$exe = Join-Path $root 'hookshot.exe'
if (!(Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'hookshot.exe is missing.' }
if (Get-Process hookshot -ErrorAction SilentlyContinue) { throw 'Close the existing game before starting a capture.' }
$out = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputDirectory)
if (Test-Path -LiteralPath $out) { throw 'Choose a new capture directory.' }
[void][IO.Directory]::CreateDirectory($out)
$frameLog = Join-Path $out 'presents.csv'
$stderr = Join-Path $out 'renderer.log'
$start = New-Object System.Diagnostics.ProcessStartInfo
$start.FileName = $exe
$start.WorkingDirectory = $root
$start.UseShellExecute = $false
$start.RedirectStandardError = $true
$start.EnvironmentVariables['RX_VK_FRAME_LOG'] = $frameLog
if ($PassTiming) { $start.EnvironmentVariables['RX_VK_PASS_TIMING'] = '1' }
$process = [Diagnostics.Process]::Start($start)
$log = [IO.File]::Create($stderr)
try {
    $copy = $process.StandardError.BaseStream.CopyToAsync($log)
    Write-Host 'Play the comparison scene, then close the game to finish the capture.'
    $process.WaitForExit()
    $copy.GetAwaiter().GetResult()
} finally {
    $log.Dispose()
    $process.Dispose()
}
if ((Test-Path -LiteralPath $frameLog) -and @(Import-Csv -LiteralPath $frameLog).Count -ge 3) {
    & "$PSScriptRoot/Measure-FrameTimes.ps1" -CsvPath $frameLog |
        ConvertTo-Json | Set-Content -LiteralPath (Join-Path $out 'session-summary.json') -Encoding UTF8
}
Select-String -LiteralPath $stderr -Pattern 'provider dispatched|fsr3.*frames drawn|FSR 3.1 fallback|first negative VkResult|destroyed frame|GPU pass timing|FSR 4 SDK dispatch|memory heaps|compaction.*over' |
    ForEach-Object Line | Set-Content -LiteralPath (Join-Path $out 'diagnostics.txt') -Encoding UTF8
