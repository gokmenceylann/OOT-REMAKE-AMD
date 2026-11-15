#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ExeFS,
    [Parameter(Mandatory)][string]$RomFS,
    [Parameter(Mandatory)][string]$LocalRoot,
    [Parameter(Mandatory)][string]$Python,
    [Parameter(Mandatory)][string]$LlvmMingw,
    [Parameter(Mandatory)][string]$Cpm,
    [switch]$EnableFsr412,
    [switch]$EnableMemoryOptimization,
    [switch]$EnablePerformanceAudit,
    [ValidateRange(1,32)][int]$Jobs = 8
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot
$source = Join-Path $repo 'upstream/mako'
$expected = 'b77ac86187330eb7447ac65ab23187baac4600ca'
$patches = @(
    (Join-Path $repo 'patches/fg-present-recovery.patch'),
    (Join-Path $repo 'patches/pipeline-performance.patch'),
    (Join-Path $repo 'patches/pipeline-slow-key.patch'),
    (Join-Path $repo 'patches/pipeline-recent-warmup.patch'),
    (Join-Path $repo 'patches/pipeline-region-warmup.patch'),
    (Join-Path $repo 'patches/pipeline-region-use.patch'),
    (Join-Path $repo 'patches/fg-incomplete-frame.patch')
)
if ($EnableFsr412) { $patches += Join-Path $repo 'patches/fsr-4.1.2.patch' }
if ($EnableMemoryOptimization) { $patches += Join-Path $repo 'patches/rx6700m-memory.patch' }
if ($EnablePerformanceAudit) { $patches += Join-Path $repo 'patches/performance-audit.patch' }
$builder = Join-Path $source 'nx2/make_game.py'
if (-not (Test-Path -LiteralPath $builder -PathType Leaf)) {
    throw 'Initialize upstream with git submodule update --init.'
}
$actual = git -C $source rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $actual -ne $expected) { throw "Expected Mako revision $expected." }
$root = [IO.Path]::GetFullPath($ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($LocalRoot))
$repo = [IO.Path]::GetFullPath($repo)
if ($root.Equals($repo, 'OrdinalIgnoreCase') -or $root.StartsWith($repo + '\', 'OrdinalIgnoreCase')) {
    throw 'Use a build directory outside the source checkout.'
}
$exefs = (Resolve-Path -LiteralPath $ExeFS).Path
$romfs = (Resolve-Path -LiteralPath $RomFS).Path
foreach ($inputPath in @($exefs, $romfs)) {
    if ($inputPath.Equals($root, 'OrdinalIgnoreCase') -or
        $inputPath.StartsWith($root + '\', 'OrdinalIgnoreCase') -or
        $root.StartsWith($inputPath + '\', 'OrdinalIgnoreCase')) {
        throw 'The source files and local build directory must be separate.'
    }
}
$pythonExe = (Resolve-Path -LiteralPath $Python).Path
$mingwPath = (Resolve-Path -LiteralPath $LlvmMingw).Path
$cpmPath = (Resolve-Path -LiteralPath $Cpm).Path
[void][IO.Directory]::CreateDirectory($root)
$oldMingw = $env:HOOKSHOT_MINGW
$oldCpm = $env:RX_CPM
$oldUpdate = $env:HOOKSHOT_NO_UPDATE_CHECK
try {
    $env:HOOKSHOT_MINGW = $mingwPath
    $env:RX_CPM = $cpmPath
    $env:HOOKSHOT_NO_UPDATE_CHECK = '1'
    $fsrArgs = @()
    foreach ($patch in $patches) {
        git -C $source apply --ignore-whitespace --reverse --check $patch 2>$null
        if ($LASTEXITCODE -ne 0) {
            git -C $source apply --ignore-whitespace --check $patch
            if ($LASTEXITCODE -ne 0) { throw "Cannot apply patch to this checkout: $patch" }
            git -C $source apply --ignore-whitespace $patch
            if ($LASTEXITCODE -ne 0) { throw 'Patch failed: $patch' }
        }
    }
    if ($EnableFsr412) { $fsrArgs = @('--fsr') }
    & $pythonExe -I $builder @fsrArgs --exefs $exefs --romfs $romfs `
        --out (Join-Path $root game) --work (Join-Path $root build) --jobs $Jobs `
        --no-prepare-shaders --log (Join-Path $root build.log)
    if ($LASTEXITCODE -ne 0) { throw "Mako build failed with exit code $LASTEXITCODE." }
}
finally {
    $env:HOOKSHOT_MINGW = $oldMingw
    $env:RX_CPM = $oldCpm
    $env:HOOKSHOT_NO_UPDATE_CHECK = $oldUpdate
}
