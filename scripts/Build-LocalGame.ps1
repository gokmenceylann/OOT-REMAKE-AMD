#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ExeFS,
    [Parameter(Mandatory)][string]$RomFS,
    [Parameter(Mandatory)][string]$LocalRoot,
    [Parameter(Mandatory)][string]$Python,
    [Parameter(Mandatory)][string]$LlvmMingw,
    [Parameter(Mandatory)][string]$Cpm,
    [ValidateRange(1,32)][int]$Jobs = 8
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot
$source = Join-Path $repo 'upstream/mako'
$expected = 'bef2014454a9a3e669c77cb4e6cfb4b04f362f3a'
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
    & $pythonExe -I $builder --exefs $exefs --romfs $romfs `
        --out (Join-Path $root game) --work (Join-Path $root build) --jobs $Jobs `
        --no-prepare-shaders --log (Join-Path $root build.log)
    if ($LASTEXITCODE -ne 0) { throw "Mako build failed with exit code $LASTEXITCODE." }
}
finally {
    $env:HOOKSHOT_MINGW = $oldMingw
    $env:RX_CPM = $oldCpm
    $env:HOOKSHOT_NO_UPDATE_CHECK = $oldUpdate
}
