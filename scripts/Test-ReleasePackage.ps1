#Requires -Version 5.1
param(
    [Parameter(Mandatory)][string]$PackageDirectory,
    [string]$ExpectedRuntimeManifest
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $PackageDirectory).Path
$manifest = @(Get-Content -LiteralPath (Join-Path $root 'SHA256SUMS.txt'))
if ($manifest.Count -lt 1 -or $manifest.Count -gt 2) { throw 'Unexpected manifest count.' }
foreach ($line in $manifest) {
    if ($line -notmatch '^([0-9a-f]{64})  (OOT-REMAKE-AMD-v\d+\.\d+\.\d+(?:-rc\.[1-9]\d*)?-(?:tools|game-import)(?:\.zip|-setup\.exe))$') {
        throw "Invalid checksum line: $line"
    }
    $expected = $Matches[1]
    if ((Get-FileHash -LiteralPath (Join-Path $root $Matches[2])).Hash -ne $expected) { throw 'Checksum mismatch.' }
}
$zip = @(Get-ChildItem -LiteralPath $root -Filter 'OOT-REMAKE-AMD-*.zip' -File)
if ($zip.Count -ne 1) { throw 'Expected one package ZIP.' }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [IO.Compression.ZipFile]::OpenRead($zip[0].FullName)
try {
    $entries = @($archive.Entries | Where-Object Name | ForEach-Object { $_.FullName.Replace('\','/') })
    foreach ($name in 'README.md','README.tr.md','LICENSE','THIRD-PARTY.md','VERSION.txt','scripts/Test-LocalGame.ps1','scripts/Import-LocalGame.ps1','scripts/Capture-VulkanSession.ps1','scripts/Measure-FrameTimes.ps1') {
        if ($name -notin $entries) { throw "Missing ZIP member: $name" }
    }
    if ($entries -match '(?i)\.(exe|dll|nup|nso|nca|xci|keys|bin)$|(^|/)(romfs|exefs|user)/') {
        throw 'Unexpected game or binary files in the package ZIP.'
    }
    if ($zip[0].Name -notmatch '^OOT-REMAKE-AMD-(v.+)-(tools|game-import)\.zip$') {
        throw 'Unexpected package ZIP name.'
    }
    $version = $Matches[1]
    if ($ExpectedRuntimeManifest -and ($Matches[2] -ne 'game-import' -or $manifest.Count -ne 2 -or
        !(Test-Path -LiteralPath (Join-Path $root "OOT-REMAKE-AMD-$version-game-import-setup.exe") -PathType Leaf))) {
        throw 'Expected a game import ZIP and installer.'
    }
    $reader = [IO.StreamReader]::new($archive.GetEntry('VERSION.txt').Open())
    try {
        if ($reader.ReadToEnd().Trim() -cne $version) { throw 'Packaged version mismatch.' }
    } finally { $reader.Dispose() }
    if ($ExpectedRuntimeManifest) {
        $entry = $archive.GetEntry('STABLE-RUNTIME-SHA256.txt')
        if (!$entry) { throw 'Missing exact-runtime manifest.' }
        $reader = [IO.StreamReader]::new($entry.Open())
        try {
            if ($reader.ReadToEnd().Trim() -cne (Get-Content -LiteralPath $ExpectedRuntimeManifest -Raw).Trim()) {
                throw 'Packaged runtime manifest mismatch.'
            }
        } finally { $reader.Dispose() }
    }
} finally { $archive.Dispose() }
try {
    & "$PSScriptRoot/Test-LocalGame.ps1" -GameDirectory $root
    throw 'Preflight accepted a directory without game data.'
} catch {
    if ($_.Exception.Message -notlike 'Local build is incomplete.*') { throw }
}
Write-Output 'Package archive, SHA-256 and missing-data checks passed.'
