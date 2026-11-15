#Requires -Version 5.1
param(
    [Parameter(Mandatory)][string]$Clang,
    [Parameter(Mandatory)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$root = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputDirectory)
if (Test-Path -LiteralPath $root) { throw 'Choose a new fixture directory.' }
[void][IO.Directory]::CreateDirectory($root)
$fixture = Join-Path $root 'fixture.c'
@"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    const char *mode = getenv("RX_CAPTURE_TEST_MODE");
    if (!mode) return 1;
    if (!strcmp(mode, "stderr")) fputs("vk: fixture initialized\n", stderr);
    if (!strcmp(mode, "native") || !strcmp(mode, "nested")) {
        const char *path = !strcmp(mode, "nested") ? "logs/hookshot_log.txt" : "hookshot_log.txt";
        FILE *log = fopen(path, "w");
        if (!log) return 2;
        fputs("vk: native log\n", log);
        fclose(log);
    }
    FILE *csv = fopen(getenv("RX_VK_FRAME_LOG"), "w");
    if (!csv) return 3;
    fputs("frame,time_s,frametime_ms\n1,0,0\n2,1,16\n3,2,18\n", csv);
    fclose(csv);
    return 0;
}
"@ | Set-Content -LiteralPath $fixture -Encoding ASCII
& $Clang $fixture -o (Join-Path $root 'hookshot.exe')
if ($LASTEXITCODE -ne 0) { throw 'Fixture compilation failed.' }
[void][IO.Directory]::CreateDirectory((Join-Path $root 'logs'))
$oldMode = $env:RX_CAPTURE_TEST_MODE
try {
    foreach ($mode in 'stderr','native','nested','empty') {
        $env:RX_CAPTURE_TEST_MODE = $mode
        $out = Join-Path $root $mode
        $errorMessage = $null
        try {
            & "$PSScriptRoot/../scripts/Capture-VulkanSession.ps1" -GameDirectory $root -OutputDirectory $out -SkipSeconds 1
        } catch {
            $errorMessage = $_.Exception.Message
        }
        $session = Get-Content -Raw -LiteralPath (Join-Path $out 'session.json') | ConvertFrom-Json
        $summary = Join-Path $out 'session-summary.json'
        if ($mode -eq 'empty') {
            if ($errorMessage -notlike 'No renderer messages*' -or !$session.Failure -or (Test-Path -LiteralPath $summary)) {
                throw 'An empty capture must fail even when a stale native log and a valid CSV exist.'
            }
            continue
        }
        $expectedSource = if ($mode -eq 'stderr') { 'stderr' } else { 'native-file' }
        if ($errorMessage -or $session.RendererLogLines -ne 1 -or $session.ExitCode -ne 0 -or
            $session.RendererLogSource -ne $expectedSource) {
            throw "Unexpected capture result for $mode. $errorMessage"
        }
        $stats = Get-Content -Raw -LiteralPath $summary | ConvertFrom-Json
        if ($stats.SampleCount -ne 2 -or $stats.AverageFrameTimeMs -ne 17) { throw 'Unexpected window statistics.' }
    }
} finally {
    $env:RX_CAPTURE_TEST_MODE = $oldMode
}
Write-Output 'Capture stderr, native recovery, stale file rejection and frame-window checks passed.'
