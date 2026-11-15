#Requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$GameDirectory,
    [Parameter(Mandatory)][string]$BackupRoot
)
$ErrorActionPreference = 'Stop'
$game = (Resolve-Path -LiteralPath $GameDirectory).Path.TrimEnd('\')
$root = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($BackupRoot).TrimEnd('\')
if ($root -eq $game -or $root.StartsWith($game + '\', 'OrdinalIgnoreCase')) { throw 'Use a backup root outside the game.' }
if (Get-Process hookshot -ErrorAction SilentlyContinue) { throw 'Close Hookshot before backing up a consistent snapshot.' }
$backup = Join-Path $root ('OOT-REMAKE-AMD-' + [DateTime]::Now.ToString('yyyy-MM-dd_HHmmssfff'))
[void][IO.Directory]::CreateDirectory($backup)
$files = @(Get-ChildItem -LiteralPath $game -File -Force | Where-Object { $_.Name -match '^(?:hookshot\.exe|.+\.dll|.+\.ini|hookshot_env\.txt|hookshot_version\.txt|language\.txt|image\.bin|hookshot_.*\.bin|\.hookshot_fsr)$' })
$pending = [Collections.Generic.Stack[string]]::new()
foreach ($relative in 'user','SAVE FOLDER','cache') {
    $directory = Join-Path $game $relative
    if (Test-Path -LiteralPath $directory -PathType Container) { $pending.Push($directory) }
}
while ($pending.Count) {
    $directory = Get-Item -LiteralPath $pending.Pop() -Force
    if ($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Back up linked data explicitly: $($directory.FullName)" }
    foreach ($item in Get-ChildItem -LiteralPath $directory.FullName -Force) {
        if ($item.PSIsContainer) { $pending.Push($item.FullName) } else { $files += $item }
    }
}
foreach ($name in 'hookshot.exe','hookshot_vk.dll') {
    if (!(Get-Item -LiteralPath (Join-Path $game $name) -ErrorAction SilentlyContinue).Length) { throw "Missing runtime file: $name" }
}
$inventory = foreach ($file in Get-ChildItem -LiteralPath $game -Force) {
    [pscustomobject]@{ Name = $file.Name; Attributes = $file.Attributes.ToString(); Length = $file.Length }
}
$manifest = foreach ($file in $files) {
    if ($file.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Back up linked data explicitly: $($file.FullName)" }
    $relative = $file.FullName.Substring($game.Length + 1)
    $dest = Join-Path $backup $relative
    [void][IO.Directory]::CreateDirectory((Split-Path $dest))
    $sha = (Get-FileHash -LiteralPath $file.FullName).Hash
    Copy-Item -LiteralPath $file.FullName -Destination $dest
    if ((Get-FileHash -LiteralPath $dest).Hash -ne $sha) { throw "Backup verification failed: $relative" }
    [pscustomobject]@{ Path = $relative; Bytes = $file.Length; SHA256 = $sha }
}
if (Get-Process hookshot -ErrorAction SilentlyContinue) { throw 'Hookshot opened before the backup completed.' }
$inventory | Export-Csv -LiteralPath (Join-Path $backup 'inventory.csv') -NoTypeInformation -Encoding UTF8
$manifest | Export-Csv -LiteralPath (Join-Path $backup 'sha256.csv') -NoTypeInformation -Encoding UTF8
[IO.File]::WriteAllText((Join-Path $backup 'game-directory.txt'), $game)
Write-Output $backup
