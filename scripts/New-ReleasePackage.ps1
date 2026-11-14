#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('\Av\d+\.\d+\.\d+\z')][string]$Version,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [string]$InnoCompiler
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot
$out = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputDirectory)
[void][IO.Directory]::CreateDirectory($out)
$base = "OOT-REMAKE-AMD-$Version"
$zip = Join-Path $out "$base-tools.zip"
$setup = Join-Path $out "$base-tools-setup.exe"
$checksums = Join-Path $out 'SHA256SUMS.txt'
foreach ($file in @($zip, $setup, $checksums)) {
    if (Test-Path -LiteralPath $file) { throw "Output already exists: $file" }
}
$stage = Join-Path ([IO.Path]::GetTempPath()) ("oot-release-" + [guid]::NewGuid())
[void][IO.Directory]::CreateDirectory($stage)
try {
    $payload = Join-Path $stage 'payload'
    [void][IO.Directory]::CreateDirectory($payload)
    $files = @(
        'README.md', 'README.tr.md', 'LICENSE', 'THIRD-PARTY.md',
        'CHANGELOG.md', 'docs/install.md', 'docs/mako-build.md', 'docs/fsr-4.1.2.md',
        'docs/fsr-context-recovery.md', 'docs/known-issues.md', 'docs/troubleshooting.md',
        'docs/memory-telemetry.md', 'docs/vulkan-memory.md', 'docs/validation-rx6700m.md',
        'docs/release.md', 'CONTRIBUTING.md', 'scripts/Test-LocalGame.ps1', 'scripts/Measure-FrameTimes.ps1', 'docs/amd-compatibility.md', 'upstream/mako/LICENSE'
    )
    foreach ($relative in $files) {
        $source = Join-Path $repo $relative
        $item = Get-Item -LiteralPath $source
        if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Expected a regular source file: $relative"
        }
        $destination = Join-Path $payload $relative
        [void][IO.Directory]::CreateDirectory((Split-Path $destination))
        Copy-Item -LiteralPath $source -Destination $destination
    }
    Set-Content -LiteralPath (Join-Path $payload 'VERSION.txt') -Value $Version -Encoding ASCII
    $archive = Join-Path $stage "$base-tools.zip"
    Compress-Archive -Path (Join-Path $payload '*') -DestinationPath $archive
    $artifacts = @($archive)
    if ($InnoCompiler) {
        $compiler = (Resolve-Path -LiteralPath $InnoCompiler).Path
        & $compiler "/DPackageVersion=$($Version.Substring(1))" "/DPayload=$payload" "/O$stage" "/F$base-tools-setup" (Join-Path $repo 'installer/Tools.iss')
        if ($LASTEXITCODE -ne 0) { throw "ISCC failed with exit code $LASTEXITCODE." }
        $artifacts += Join-Path $stage "$base-tools-setup.exe"
    }
    $entries = foreach ($artifact in $artifacts) {
        $hash = Get-FileHash -LiteralPath $artifact -Algorithm SHA256
        "$($hash.Hash.ToLowerInvariant())  $(Split-Path -Leaf $artifact)"
    }
    $entries | Set-Content -LiteralPath (Join-Path $stage 'SHA256SUMS.txt') -Encoding ASCII
    foreach ($artifact in $artifacts + @((Join-Path $stage 'SHA256SUMS.txt'))) {
        Move-Item -LiteralPath $artifact -Destination $out
    }
    Get-ChildItem -LiteralPath $out -File | Where-Object Name -in @((Split-Path -Leaf $zip), (Split-Path -Leaf $setup), 'SHA256SUMS.txt')
}
finally {
    $fullStage = [IO.Path]::GetFullPath($stage)
    $tempPrefix = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\oot-release-'
    if ($fullStage.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $fullStage -Recurse -Force
    }
}
