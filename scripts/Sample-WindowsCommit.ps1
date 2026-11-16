#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateRange(1,2147483647)][int]$GameProcessId,
    [Parameter(Mandatory)][string]$CsvPath,
    [ValidateRange(1,60)][int]$IntervalSeconds = 5,
    [ValidateRange(1,7200)][int]$DurationSeconds = 1800,
    [switch]$IncludeMakoAddressSpace
)
$ErrorActionPreference = 'Stop'
$target = Get-Process -Id $GameProcessId
$started = $target.StartTime
$out = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($CsvPath)
if (Test-Path -LiteralPath $out) { throw 'Choose a new CSV file.' }

if ($IncludeMakoAddressSpace) {
    if (![Environment]::Is64BitProcess) { throw 'Mako address-space sampling requires 64-bit PowerShell.' }
    if (!('MakoAddressSpace' -as [type])) { Add-Type -Path (Join-Path $PSScriptRoot 'MakoAddressSpace.cs') }
}
$clock = [Diagnostics.Stopwatch]::StartNew()
do {
    $target = Get-Process -Id $GameProcessId -ErrorAction SilentlyContinue
    if (!$target -or $target.StartTime -ne $started) { break }
    $utc = [DateTimeOffset]::UtcNow
    $game = Get-CimInstance Win32_PerfRawData_PerfProc_Process -Filter "IDProcess = $GameProcessId"
    $system = Get-CimInstance Win32_PerfRawData_PerfOS_Memory
    if ($game) {
        $row = [ordered]@{
            Utc = $utc.ToString('o')
            ProcessId = $GameProcessId
            Source = 'Windows PerfProc_Process and PerfOS_Memory'
            ProcessPrivateBytes = $game.PrivateBytes
            ProcessCommitBytes = $game.PageFileBytes
            ProcessWorkingSetBytes = $game.WorkingSet
            SystemCommittedBytes = $system.CommittedBytes
            SystemCommitLimitBytes = $system.CommitLimit
        }
        if ($IncludeMakoAddressSpace) {
            $query = [Diagnostics.Stopwatch]::StartNew()
            try {
                $regions = [MakoAddressSpace]::Query($GameProcessId)
            } catch {
                if (!(Get-Process -Id $GameProcessId -ErrorAction SilentlyContinue)) { break }
                throw
            }
            $row.GuestCommittedRegionBytes = $regions[0]
            $row.HostPrivateRegionBytes = $regions[1]
            $row.HostMappedRegionBytes = $regions[2]
            $row.HostImageRegionBytes = $regions[3]
            $row.AddressSpaceQueryMs = [Math]::Round($query.Elapsed.TotalMilliseconds, 2)
        }
        [pscustomobject]$row | Export-Csv -LiteralPath $out -NoTypeInformation -Append
    }
    $remaining = $DurationSeconds - $clock.Elapsed.TotalSeconds
    if ($remaining -gt 0) {
        Start-Sleep -Milliseconds ([int](1000 * [Math]::Min($IntervalSeconds, $remaining)))
    }
} while ($clock.Elapsed.TotalSeconds -lt $DurationSeconds)
