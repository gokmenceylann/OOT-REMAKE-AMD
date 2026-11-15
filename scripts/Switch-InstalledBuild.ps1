#Requires -Version 5.1
[CmdletBinding(DefaultParameterSetName='Deploy')]
param(
    [Parameter(Mandatory)][string]$GameDirectory,
    [Parameter(Mandatory)][string]$BackupDirectory,
    [Parameter(Mandatory,ParameterSetName='Deploy')][string]$StagingDirectory,
    [Parameter(Mandatory,ParameterSetName='Restore')][switch]$Restore
)
$ErrorActionPreference = 'Stop'
$game = (Resolve-Path -LiteralPath $GameDirectory).Path
$backup = (Resolve-Path -LiteralPath $BackupDirectory).Path
if ((Get-Content -Raw -LiteralPath (Join-Path $backup 'game-directory.txt')) -ne $game) {
    throw 'The backup belongs to a different game directory.'
}
if (Get-Process hookshot -ErrorAction SilentlyContinue) { throw 'Close Hookshot before replacing the binaries.' }
$manifest = @(Import-Csv -LiteralPath (Join-Path $backup 'sha256.csv'))
foreach ($file in $manifest) {
    $path = [IO.Path]::GetFullPath((Join-Path $backup $file.Path))
    if (!$path.StartsWith($backup + '\', 'OrdinalIgnoreCase') -or
        (Get-FileHash -LiteralPath $path).Hash -ne $file.SHA256) { throw "Backup verification failed: $($file.Path)" }
}
$source = if ($Restore) { $backup } else { (Resolve-Path -LiteralPath $StagingDirectory).Path }
if ($source -eq $game) { throw 'Use a separate staging directory.' }
$names = 'hookshot.exe', 'hookshot_vk.dll'
$id = [Guid]::NewGuid().ToString('N')
$changes = @(foreach ($name in $names) {
    $before = @($manifest | Where-Object Path -eq $name)
    if ($before.Count -ne 1) { throw "Backup is missing $name." }
    $from = Get-Item -LiteralPath (Join-Path $source $name)
    $to = Get-Item -LiteralPath (Join-Path $game $name)
    if ($from.PSIsContainer -or $to.PSIsContainer -or !$from.Length -or
        (($from.Attributes -bor $to.Attributes) -band [IO.FileAttributes]::ReparsePoint)) { throw "Invalid runtime file: $name" }
    $want = (Get-FileHash -LiteralPath $from.FullName).Hash
    $current = (Get-FileHash -LiteralPath $to.FullName).Hash
    if (!$Restore -and $current -ne $before[0].SHA256) { throw "Installed file changed since backup: $name" }
    if ($want -ne $current) {
        [pscustomobject]@{ Name=$name; From=$from.FullName; To=$to.FullName; Hash=$want; OldHash=$current
            Temp="$($to.FullName).$id.new"; Old="$($to.FullName).$id.old"; Renamed=$false; Installed=$false }
    }
})
try {
    foreach ($change in $changes) {
        Copy-Item -LiteralPath $change.From -Destination $change.Temp
        if ((Get-FileHash -LiteralPath $change.Temp).Hash -ne $change.Hash) { throw "Staging verification failed: $($change.Name)" }
    }
    if (Get-Process hookshot -ErrorAction SilentlyContinue) { throw 'Hookshot opened during staging.' }
    foreach ($change in $changes) {
        Rename-Item -LiteralPath $change.To -NewName (Split-Path -Leaf $change.Old)
        $change.Renamed = $true
        Rename-Item -LiteralPath $change.Temp -NewName $change.Name
        $change.Installed = $true
        if ((Get-FileHash -LiteralPath $change.To).Hash -ne $change.Hash) { throw "Installed verification failed: $($change.Name)" }
    }
} catch {
    foreach ($change in $changes) {
        if ($change.Installed) { Rename-Item -LiteralPath $change.To -NewName (Split-Path -Leaf $change.Temp) }
        if ($change.Renamed) {
            Rename-Item -LiteralPath $change.Old -NewName $change.Name
            if ((Get-FileHash -LiteralPath $change.To).Hash -ne $change.OldHash) { throw "Rollback verification failed: $($change.Name)" }
        }
    }
    throw
} finally {
    foreach ($change in $changes) {
        if (Test-Path -LiteralPath $change.Temp) { Remove-Item -LiteralPath $change.Temp -ErrorAction Continue }
    }
}
foreach ($change in $changes) {
    Remove-Item -LiteralPath $change.Old -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $change.Old) { Write-Warning "Windows retained the prior file: $($change.Old)" }
    [pscustomobject]@{ File=$change.To; SHA256=$change.Hash }
}
