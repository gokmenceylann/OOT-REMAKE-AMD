#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$CsvPath,
    [ValidateRange(0,86400)][double]$SkipSeconds = 0,
    [ValidateRange(0,86400)][double]$DurationSeconds = 0
)
$ErrorActionPreference = 'Stop'
$culture = [Globalization.CultureInfo]::InvariantCulture
$rows = @(Import-Csv -LiteralPath $CsvPath)
if (!$rows.Count -or 'frametime_ms' -notin $rows[0].PSObject.Properties.Name -or
    'time_s' -notin $rows[0].PSObject.Properties.Name) {
    throw 'Expected the Vulkan RX_VK_FRAME_LOG CSV.'
}
$times = @(foreach ($row in $rows) {
    $t = [double]::Parse($row.time_s, $culture)
    $ms = [double]::Parse($row.frametime_ms, $culture)
    if ($ms -gt 0 -and -not [double]::IsInfinity($ms) -and
        $t -ge $SkipSeconds -and (!$DurationSeconds -or $t -lt ($SkipSeconds + $DurationSeconds))) { $ms }
})
if ($times.Count -lt 2) { throw 'At least two measured frame intervals are required.' }
$sorted = @($times | Sort-Object)
function Get-TailFps([double]$Fraction) {
    $count = [int][Math]::Ceiling($sorted.Count * $Fraction)
    if ($count -lt 2) { return }
    $mean = ($sorted | Select-Object -Last $count | Measure-Object -Average).Average
    [Math]::Round(1000 / $mean, 2)
}
[pscustomobject]@{
    SampleCount = $sorted.Count
    AverageFps = [Math]::Round(1000 / ($times | Measure-Object -Average).Average, 2)
    Low1PercentFps = Get-TailFps 0.01
    LowPoint1PercentFps = Get-TailFps 0.001
    P95Ms = $sorted[[int][Math]::Ceiling(0.95 * $sorted.Count) - 1]
    P99Ms = $sorted[[int][Math]::Ceiling(0.99 * $sorted.Count) - 1]
    Over60FpsBudget = @($times | Where-Object { $_ -gt (1000 / 60) }).Count
}
