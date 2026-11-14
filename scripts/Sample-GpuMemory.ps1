#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateRange(1,2147483647)][int]$GameProcessId,
    [ValidateRange(1,120)][int]$IntervalSeconds = 5,
    [ValidateRange(1,360)][int]$Samples = 12,
    [string]$CsvPath
)
$ErrorActionPreference = 'Stop'
$game = Get-Process -Id $GameProcessId
if ($CsvPath -and (Test-Path -LiteralPath $CsvPath)) { throw 'Choose a new CSV path.' }
for ($index = 0; $index -lt $Samples; $index++) {
    if ($game.HasExited) { break }
    $time = [DateTime]::UtcNow.ToString('o')
    $rows = @(Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUProcessMemory |
        Where-Object { $_.Name -like "pid_${GameProcessId}_*" } |
        ForEach-Object {
            [pscustomobject]@{
                Utc = $time
                Source = 'Windows WDDM GPU Process Memory (CIM)'
                Instance = $_.Name
                DedicatedUsageBytes = $_.DedicatedUsage
                SharedUsageBytes = $_.SharedUsage
                TotalCommittedBytes = $_.TotalCommitted
                LocalUsageBytes = $_.LocalUsage
                NonLocalUsageBytes = $_.NonLocalUsage
            }
        })
    if ($rows.Count -and $CsvPath) { $rows | Export-Csv -LiteralPath $CsvPath -Append -NoTypeInformation }
    $rows
    if ($index + 1 -lt $Samples) { Start-Sleep -Seconds $IntervalSeconds }
}
