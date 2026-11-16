#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$GameDirectory,
    [string]$Destination,
    [switch]$CheckOnly,
    [string]$RuntimeManifest,
    [string]$ErrorLog
)
$ErrorActionPreference = 'Stop'
trap {
    if ($ErrorLog) { [IO.File]::WriteAllText($ErrorLog, $_.Exception.Message, (New-Object Text.UTF8Encoding($false))) }
    throw $_
}
$source = (Resolve-Path -LiteralPath $GameDirectory).Path
$required = 'hookshot.exe', 'hookshot_vk.dll', 'image.bin'
$optional = 'hookshot_shaders.bin', 'hookshot_pipeline_states_shipped.bin', 'hookshot_version.txt',
            'SDL2.dll', 'SDL3.dll', 'libwinpthread-1.dll', 'language.txt'
foreach ($name in $required) {
    $file = Get-Item -LiteralPath (Join-Path $source $name) -ErrorAction SilentlyContinue
    if (!$file -or $file.PSIsContainer -or !$file.Length) { throw "Missing $name. Select a complete local Hookshot build." }
}
$romfs = Join-Path $source 'romfs'
if (!(Test-Path -LiteralPath $romfs -PathType Container) -or !(Get-ChildItem -LiteralPath $romfs -Force | Select-Object -First 1)) {
    throw 'Missing or empty romfs directory. Supply RomFS from your own matching game dump.'
}
foreach ($name in 'hookshot.exe', 'hookshot_vk.dll') {
    $reader = New-Object IO.BinaryReader([IO.File]::OpenRead((Join-Path $source $name)))
    try {
        if ($reader.ReadUInt16() -ne 0x5a4d -or $reader.BaseStream.Length -lt 64) { throw "Invalid Windows binary: $name" }
        $reader.BaseStream.Position = 60
        $offset = $reader.ReadUInt32()
        if ($offset -gt $reader.BaseStream.Length - 6) { throw "Invalid PE header: $name" }
        $reader.BaseStream.Position = $offset
        if ($reader.ReadUInt32() -ne 0x4550 -or $reader.ReadUInt16() -ne 0x8664) { throw "Expected Windows x64: $name" }
    } finally { $reader.Dispose() }
}
if (!$RuntimeManifest) {
    $packagedManifest = Join-Path (Split-Path $PSScriptRoot) 'STABLE-RUNTIME-SHA256.txt'
    if (Test-Path -LiteralPath $packagedManifest -PathType Leaf) { $RuntimeManifest = $packagedManifest }
}
if ($RuntimeManifest) {
    $expected = @{}
    foreach ($line in Get-Content -LiteralPath $RuntimeManifest) {
        if ($line -notmatch '^([0-9a-fA-F]{64})  (hookshot\.exe|hookshot_vk\.dll)$' -or $expected.ContainsKey($Matches[2])) {
            throw 'Invalid stable runtime manifest.'
        }
        $expected[$Matches[2]] = $Matches[1]
    }
    foreach ($name in 'hookshot.exe', 'hookshot_vk.dll') {
        $algorithm = [Security.Cryptography.SHA256]::Create()
        $stream = [IO.File]::OpenRead((Join-Path $source $name))
        try {
            $hash = [BitConverter]::ToString($algorithm.ComputeHash($stream)).Replace('-', '')
        } finally {
            $stream.Dispose()
            $algorithm.Dispose()
        }
        if (!$expected.ContainsKey($name) -or $hash -ne $expected[$name]) {
            throw "$name does not match the verified Mako 4.1.1 baseline. Select the matching local build documented for this package."
        }
    }
}
$system = Join-Path $env:WINDIR 'System32'
foreach ($dep in @{
    'ucrtbase.dll' = 'Install current Windows 11 updates to restore the Universal CRT.'
    'mfplat.dll' = 'Install Media Feature Pack from Windows Optional Features, then restart.'
    'vulkan-1.dll' = 'Install a current Vulkan-capable GPU driver.'
}.GetEnumerator()) {
    if (!(Test-Path -LiteralPath (Join-Path $system $dep.Key) -PathType Leaf)) { throw "Missing $($dep.Key). $($dep.Value)" }
}
if ($CheckOnly) { return }
if (!$Destination) { throw 'Provide -Destination for the portable game folder.' }
$dest = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Destination).TrimEnd('\')
if ($dest -eq $source -or $dest.StartsWith($source + '\', 'OrdinalIgnoreCase') -or
    $source.StartsWith($dest + '\', 'OrdinalIgnoreCase')) { throw 'Select a separate destination outside the source game folder.' }
if ((Test-Path -LiteralPath (Join-Path $dest 'hookshot.exe')) -or (Test-Path -LiteralPath (Join-Path $dest 'romfs'))) {
    throw 'Choose a new game destination. Move an existing installation separately.'
}
$packageVersion = Join-Path (Split-Path $PSScriptRoot) 'VERSION.txt'
if ((Test-Path -LiteralPath $packageVersion -PathType Leaf) -and
    (Get-Content -LiteralPath $packageVersion -Raw).Trim() -in 'v0.1.6', 'v0.2.0-rc.4') {
    $fsr = 'amd_fidelityfx_loader_vk.dll', 'amd_fidelityfx_upscaler_vk.dll'
    if (@($fsr | Where-Object { Test-Path -LiteralPath (Join-Path $source $_) -PathType Leaf }).Count -eq 2) {
        $optional += $fsr
    }
}
[void][IO.Directory]::CreateDirectory($dest)
$romOut = Join-Path $dest 'romfs'
& robocopy.exe $romfs $romOut /E /XJ /R:0 /W:0 /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8) { throw 'RomFS copy failed. Check the destination disk and try again in a new folder.' }
foreach ($name in @('image.bin') + $optional + @('hookshot_vk.dll', 'hookshot.exe')) {
    $file = Join-Path $source $name
    if (Test-Path -LiteralPath $file -PathType Leaf) { Copy-Item -LiteralPath $file -Destination $dest }
}
Write-Output (Join-Path $dest 'hookshot.exe')
