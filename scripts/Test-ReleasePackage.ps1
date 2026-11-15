#Requires -Version 5.1
param([Parameter(Mandatory)][string]$PackageDirectory)
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
if ($zip.Count -ne 1) { throw 'Expected one tools ZIP.' }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [IO.Compression.ZipFile]::OpenRead($zip[0].FullName)
try {
    $entries = @($archive.Entries | Where-Object Name | ForEach-Object { $_.FullName.Replace('\','/') })
    foreach ($name in 'README.md','README.tr.md','LICENSE','THIRD-PARTY.md','VERSION.txt','scripts/Test-LocalGame.ps1','scripts/Import-LocalGame.ps1','scripts/Capture-VulkanSession.ps1','scripts/Measure-FrameTimes.ps1') {
        if ($name -notin $entries) { throw "Missing ZIP member: $name" }
    }
    if ($entries -match '(?i)\.(exe|dll|nup|nso|nca|xci|keys|bin)$|(^|/)(romfs|exefs|user)/') {
        throw 'Unexpected game or binary files in the tools ZIP.'
    }
} finally { $archive.Dispose() }
try {
    & "$PSScriptRoot/Test-LocalGame.ps1" -GameDirectory $root
    throw 'Preflight accepted a directory without game data.'
} catch {
    if ($_.Exception.Message -notlike 'Local build is incomplete.*') { throw }
}
Write-Output 'Tools archive, SHA-256 and missing-data checks passed.'
