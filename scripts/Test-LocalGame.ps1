#Requires -Version 5.1
[CmdletBinding()]
param([Parameter(Mandatory)][string]$GameDirectory)
$ErrorActionPreference = 'Stop'
$dir = (Resolve-Path -LiteralPath $GameDirectory).Path
$missing = foreach ($name in 'hookshot.exe', 'hookshot_vk.dll', 'image.bin') {
    $item = Get-Item -LiteralPath (Join-Path $dir $name) -ErrorAction SilentlyContinue
    if (-not $item -or $item.PSIsContainer -or $item.Length -eq 0) { $name }
}
if (-not (Test-Path -LiteralPath (Join-Path $dir 'romfs') -PathType Container)) { $missing = @($missing) + 'romfs/' }
if ($missing) { throw "Local build is incomplete. Missing: $($missing -join ', '). See the installation guide." }
if (-not (Test-Path -LiteralPath (Join-Path $env:WINDIR 'System32/vulkan-1.dll') -PathType Leaf)) {
    Write-Warning 'Windows Vulkan loader was not found. Install a Vulkan-capable GPU driver.'
}
$amd = foreach ($name in 'amd_fidelityfx_loader_vk.dll', 'amd_fidelityfx_upscaler_vk.dll') {
    if (-not (Test-Path -LiteralPath (Join-Path $dir $name) -PathType Leaf)) { $name }
}
if ($amd) { Write-Verbose "Optional FSR DLLs absent beside the EXE: $($amd -join ', '). RX_VK_FSR_DIR can specify another folder." }
Write-Output 'Required local files exist. This check does not launch the game or test GPU compatibility.'
