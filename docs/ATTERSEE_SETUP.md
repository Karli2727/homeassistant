# Home Assistant & Netzwerk-Infrastruktur – Attersee

Stand: 24.11.2026

---

## 1. Systemübersicht & Remote Access

* **Knoten – Raspberry Pi 4 (`pi-attersee`):**
  * Lokale IP: `172.17.0.250` (am TP-Link Omada Switch / Gateway)
  * Tailscale IP: `100.71.126.43` (Online, Direkte OpenSSH-Verbindung via Key)
  * Cloudflare Tunnel: `https://attersee.familie-mai.at` (Aktiv, Status 200 OK via systemd `cloudflared.service`)
  * Home Assistant: Docker Container (Core 2024.10.4) in `/home/pi/home-assistant`
  * Omada Controller & Mosquitto MQTT: Port 1883
  * Hardware: Sonoff Zigbee 3.0 USB Dongle (`/dev/ttyUSB0`)

* **SSH-Authentifizierung:**
  * Bidirektionaler Key-Austausch zwischen `laptop-karl`, `pi-altlengbach` (`100.95.176.71`) und `pi-attersee` (`100.71.126.43`).
  * Tailscale SSH-Interception deaktiviert (`tailscale set --ssh=false`), direkter OpenSSH-Zugriff mit `~/.ssh/authorized_keys`.

---

## 2. Automatische Backup-Routine

* **Skript:** `/home/pi/scripts/backup_ha.sh`
* **Cronjob (Root):** `30 3 * * * /home/pi/scripts/backup_ha.sh` (Täglich um 03:30 Uhr)
* **Ablauf:**
  1. Erstellt komprimiertes Voll-Backup von `/home/pi/home-assistant` (inkl. Datenbank, `.storage/`, Automatisierungen, Lovelace; exkludiert Logs, Wal/Shm-Temp-Dateien).
  2. Speichert lokal unter `/home/pi/home-assistant/backups/ha_attersee_YYYYMMDD_HHMMSS.tar.gz`.
  3. Rotiert lokale Backups (Vorhaltezeit: 7 Tage).
  4. Synchronisiert per `rsync` über Tailscale automatisch auf den Pi Altlengbach nach `/home/pi/backups/attersee/`.
  5. Rotiert Offsite-Backups in Altlengbach (Vorhaltezeit: 14 Tage).
  6. Protokollierung in `/var/log/ha_backup_attersee.log`.
* **Erster Testlauf:** Erfolgreich abgeschlossen (`ha_attersee_20261124_191925.tar.gz`, 103 MB).

---

## 3. Einbindung in Pi-Nexus Monitoring

* **Knoten:** Pi-Altlengbach (`100.95.176.71`), Dienst `pi-nexus.service`.
* **Health-Check (`/home/pi/mcp-server/health_check.py`):**
  * `network.pi_attersee`: SSH/Port 22 Check via Tailscale (`100.71.126.43`) -> `ONLINE`.
  * `services.attersee_ha_web`: HTTP-Check auf `https://attersee.familie-mai.at` -> `ONLINE`.
  * `backups.attersee_backup_ok`: Prüft Aktualität (< 36 Stunden) und Mindestgröße (> 20 MB) des Offsite-Backups.
  * Tägliche Push-Benachrichtigung um 06:00 Uhr enthält ab sofort den Attersee-Status.
* **MCP Tools (`server.py`):**
  * `get_backup_status()`: Liefert Snapshots von Altlengbach und Offsite-Backups von Attersee.
  * `run_health_check()`: Umfasst alle Attersee-Komponenten.
