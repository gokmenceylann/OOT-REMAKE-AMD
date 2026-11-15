#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$GameDirectory,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [switch]$PassTiming,
    [ValidateRange(0,86400)][double]$SkipSeconds = 0,
    [ValidateRange(0,86400)][double]$DurationSeconds = 0
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
$process = $null
$started = [DateTimeOffset]::UtcNow
$clock = [Diagnostics.Stopwatch]::StartNew()
$exitCode = $null
$lineCount = 0
$lastLine = $null
$source = 'stderr'
$failure = $null
$nativeLog = Join-Path $root 'hookshot_log.txt'
$previousNativeLog = Get-Item -LiteralPath $nativeLog -ErrorAction SilentlyContinue
$stream = [IO.File]::Open($stderr, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::Read)
$writer = New-Object IO.StreamWriter($stream, (New-Object Text.UTF8Encoding($false)))
$writer.AutoFlush = $true
try {
    # Verify the destination before creating a child process.
    $writer.Flush()
    $process = [Diagnostics.Process]::Start($start)
    Write-Host 'Play the comparison scene, then close the game to finish the capture.'
    while ($null -ne ($line = $process.StandardError.ReadLine())) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $writer.WriteLine(('{0:O} {1}' -f [DateTimeOffset]::UtcNow, $line))
        $lineCount++
        $lastLine = $line
    }
    $process.WaitForExit()
    $exitCode = $process.ExitCode
    $currentNativeLog = Get-Item -LiteralPath $nativeLog -ErrorAction SilentlyContinue
    if ($lineCount -eq 0 -and $currentNativeLog -and $currentNativeLog.Length -gt 0 -and
        $currentNativeLog.LastWriteTimeUtc -ge $started.UtcDateTime -and
        (!$previousNativeLog -or $currentNativeLog.LastWriteTimeUtc -ne $previousNativeLog.LastWriteTimeUtc)) {
        $source = 'native-file'
        foreach ($line in [IO.File]::ReadLines($nativeLog)) {
            if ([string]::IsNullOrWhiteSpace($line)) { continue }
            $writer.WriteLine($line)
            $lineCount++
            $lastLine = $line
        }
    }
    if (!$lineCount) { throw 'No renderer messages in stderr or a fresh hookshot_log.txt.' }
    if ($exitCode -ne 0) { throw "hookshot.exe exited with code $exitCode." }
    if (!(Test-Path -LiteralPath $frameLog -PathType Leaf)) { throw 'No Vulkan present CSV was produced.' }
    $summary = & "$PSScriptRoot/Measure-FrameTimes.ps1" -CsvPath $frameLog -SkipSeconds $SkipSeconds -DurationSeconds $DurationSeconds
    $summary | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $out 'session-summary.json') -Encoding UTF8
} catch {
    $failure = $_.Exception.Message
    throw
} finally {
    $processId = if ($process) { $process.Id }
    if ($process) { $process.Dispose() }
    $writer.Dispose()
    [pscustomobject]@{
        Executable = $exe
        WorkingDirectory = $root
        ProcessId = $processId
        StartUtc = $started.ToString('O')
        EndUtc = [DateTimeOffset]::UtcNow.ToString('O')
        ElapsedSeconds = [Math]::Round($clock.Elapsed.TotalSeconds, 2)
        ExitCode = $exitCode
        RendererLogSource = $source
        RendererLogBytes = (Get-Item -LiteralPath $stderr).Length
        RendererLogLines = $lineCount
        LastRendererMessage = $lastLine
        SkipSeconds = $SkipSeconds
        DurationSeconds = $DurationSeconds
        PassTiming = $PassTiming.IsPresent
        Failure = $failure
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $out 'session.json') -Encoding UTF8
    Select-String -LiteralPath $stderr -Pattern 'provider dispatched|fsr3.*frames drawn|FSR 3.1 fallback|first negative VkResult|destroyed frame|GPU pass timing|GPU span|FSR 4 SDK dispatch|memory heaps|compaction.*over|pipeline.cache|shader.cache|camera.cut|history.reset|validation' |
        ForEach-Object Line | Set-Content -LiteralPath (Join-Path $out 'diagnostics.txt') -Encoding UTF8
}
