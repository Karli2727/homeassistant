# Home Assistant – Gut & Klein Schoderleh

Zentrales Konfigurations-Backup und Dokumentation für die Home-Assistant-Installation auf dem **Klein-Schoderleh-Pi** (`192.168.1.250`).

## Systemarchitektur

| Komponente | Host / IP | Rolle |
|---|---|---|
| **Klein-Schoderleh-Pi** | `192.168.1.250` | Home Assistant (Docker `homeassistant`, Config `/home/pi/homeassistant`), Pi-Nexus MCP-Server (`pi-nexus.service`, Port `8000` / `https://mcp.karl-mai.at/mcp`) |
| **Fronius Wechselrichter** | `172.17.0.146` / `172.17.0.147` | Klein-Schoderleh & Reithalle (via `get_solar_stats`) |
| **Gut-Schoderleh-Pi** | `172.17.0.154` | Mosquitto MQTT & Hof-Steuerung |
| **Synology NAS** | `192.168.1.210` | Passiver Backup-Datenspeicher |

## Repository-Struktur

- `config/` – Synchronisierte Home-Assistant-Konfiguration (`configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`, `themes/`, `blueprints/`, `.storage/core.config_entries`).
- `sync_from_pi.ps1` – PowerShell-Sync-Skript vom Pi per SSH/SCP.
- `PROJECT_STATUS.md` – Aktueller Projekt- und Aufgabenstatus.

> **Sicherheit:** `secrets.yaml`, `.storage/auth*`, Datenbanken (`*.db*`), Logs und Backups sind über `.gitignore` strikt ausgeschlossen.

## Backup & Sync

Manueller Sync vom Pi inkl. Commit & Push auf GitHub:

```powershell
.\sync_from_pi.ps1 -Push
```

Nur lokaler Abzug ohne Push:

```powershell
.\sync_from_pi.ps1
```

## Restore (Notfallwiederherstellung)

1. YAML-Dateien aus `config/` nach `/home/pi/homeassistant/` kopieren (`scp`).
2. Vor einem Container-Start Konfiguration prüfen:
   ```bash
   sudo docker exec homeassistant python -m homeassistant --script check_config --config /config
   ```
3. Container neu starten:
   ```bash
   sudo docker restart homeassistant
   ```
