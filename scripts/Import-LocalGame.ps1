#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$GameDirectory,
    [string]$Destination,
    [switch]$CheckOnly,
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
            'SDL2.dll', 'SDL3.dll', 'libwinpthread-1.dll'
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
[void][IO.Directory]::CreateDirectory($dest)
$romOut = Join-Path $dest 'romfs'
& robocopy.exe $romfs $romOut /E /XJ /R:0 /W:0 /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8) { throw 'RomFS copy failed. Check the destination disk and try again in a new folder.' }
foreach ($name in @('image.bin') + $optional + @('hookshot_vk.dll', 'hookshot.exe')) {
    $file = Join-Path $source $name
    if (Test-Path -LiteralPath $file -PathType Leaf) { Copy-Item -LiteralPath $file -Destination $dest }
}
Write-Output (Join-Path $dest 'hookshot.exe')
