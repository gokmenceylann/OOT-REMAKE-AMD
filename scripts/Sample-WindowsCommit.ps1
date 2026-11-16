#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateRange(1,2147483647)][int]$GameProcessId,
    [Parameter(Mandatory)][string]$CsvPath,
    [ValidateRange(1,60)][int]$IntervalSeconds = 5,
    [ValidateRange(1,7200)][int]$DurationSeconds = 1800
)
$ErrorActionPreference = 'Stop'
$target = Get-Process -Id $GameProcessId
$started = $target.StartTime
$out = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($CsvPath)
if (Test-Path -LiteralPath $out) { throw 'Choose a new CSV file.' }

$clock = [Diagnostics.Stopwatch]::StartNew()
do {
    $target = Get-Process -Id $GameProcessId -ErrorAction SilentlyContinue
    if (!$target -or $target.StartTime -ne $started) { break }
    $utc = [DateTimeOffset]::UtcNow
    $game = Get-CimInstance Win32_PerfRawData_PerfProc_Process -Filter "IDProcess = $GameProcessId"
    $system = Get-CimInstance Win32_PerfRawData_PerfOS_Memory
    if ($game) {
        [pscustomobject]@{
            Utc = $utc.ToString('o')
            ProcessId = $GameProcessId
            Source = 'Windows PerfProc_Process and PerfOS_Memory'
            ProcessPrivateBytes = $game.PrivateBytes
            ProcessCommitBytes = $game.PageFileBytes
            ProcessWorkingSetBytes = $game.WorkingSet
            SystemCommittedBytes = $system.CommittedBytes
            SystemCommitLimitBytes = $system.CommitLimit
        } | Export-Csv -LiteralPath $out -NoTypeInformation -Append
    }
    $remaining = $DurationSeconds - $clock.Elapsed.TotalSeconds
    if ($remaining -gt 0) {
        Start-Sleep -Milliseconds ([int](1000 * [Math]::Min($IntervalSeconds, $remaining)))
    }
} while ($clock.Elapsed.TotalSeconds -lt $DurationSeconds)
