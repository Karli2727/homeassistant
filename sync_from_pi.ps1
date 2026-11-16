<#
.SYNOPSIS
    Synchronisiert Home Assistant Konfigurationsdateien vom Klein-Schoderleh-Pi
    nach C:\Repos\homeassistant\config und pusht optional nach GitHub.
.PARAMETER Push
    Wenn gesetzt, werden Änderungen automatisch committed und nach GitHub gepusht.
#>
param(
    [switch]$Push
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigDir = Join-Path $RepoRoot "config"
$PiHost = "pi@192.168.1.250"
$RemoteBase = "/home/pi/homeassistant"
$SshOpts = @("-o", "BatchMode=yes", "-o", "ConnectTimeout=5")

New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null

Write-Host "Hole YAML- und Konfigurationsdateien von $PiHost..." -ForegroundColor Cyan

$Files = @(
    "configuration.yaml",
    "automations.yaml",
    "scripts.yaml",
    "scenes.yaml"
)

foreach ($f in $Files) {
    scp @SshOpts -q "${PiHost}:${RemoteBase}/$f" (Join-Path $ConfigDir $f)
}

# Optionale Verzeichnisse (themes, blueprints), falls vorhanden
foreach ($dir in @("themes", "blueprints")) {
    $exists = ssh @SshOpts $PiHost "test -d ${RemoteBase}/$dir && echo yes || echo no"
    if ($exists -eq "yes") {
        $localSub = Join-Path $ConfigDir $dir
        New-Item -ItemType Directory -Force -Path $localSub | Out-Null
        scp @SshOpts -rq "${PiHost}:${RemoteBase}/$dir/*" $localSub 2>$null
    }
}

# .storage Backups (core.config_entries, core.entity_registry)
$StorageDir = Join-Path $ConfigDir ".storage"
New-Item -ItemType Directory -Force -Path $StorageDir | Out-Null

ssh @SshOpts $PiHost "cat ${RemoteBase}/.storage/core.config_entries" | Set-Content -Encoding UTF8 (Join-Path $StorageDir "core.config_entries")
ssh @SshOpts $PiHost "cat ${RemoteBase}/.storage/core.entity_registry" | Set-Content -Encoding UTF8 (Join-Path $StorageDir "core.entity_registry")

Write-Host "Sync nach $ConfigDir erfolgreich abgeschlossen." -ForegroundColor Green

if ($Push) {
    Push-Location $RepoRoot
    try {
        git add -A
        $status = git status --porcelain
        if ($status) {
            $ts = Get-Date -Format "yyyy-MM-dd HH:mm"
            git commit -m "HA Config Sync ($ts)"
            git push origin main
            Write-Host "Änderungen auf GitHub gepusht." -ForegroundColor Green
        } else {
            Write-Host "Keine Änderungen gegenüber dem letzten Commit." -ForegroundColor Yellow
        }
    } finally {
        Pop-Location
    }
}
