# Gesamte Netzwerk- & Server-Infrastruktur (Gut & Klein Schoderleh)

Stand: 16.11.2026

---

## 1. Topologie & Netzwerkknoten

### A. Subnetz Klein Schoderleh (`192.168.1.0/24`)
* **Router / Gateway (`192.168.1.1`):**
  * AVM Fritz!Box (Modell FritzKlSchoderleh)
  * Wi-Fi: `Klein Schoderleh` (5 GHz Kanal 36, WPA2-CCMP)
  * NAS-Freigabe: `\\192.168.1.1\Mediaserver` (USB 3.0 Speicher `External-USB3-0-01`), auf Laptop gemountet als **`Z:`**
* **Klein-Schoderleh-Pi (`192.168.1.250`):**
  * Hardware: Raspberry Pi (Raspberry Pi OS Bookworm / Debian 12)
  * User: `pi` (Passwort: `raspberry`), SSH Public-Key Authentifizierung via Laptop `id_ed25519`
  * Services:
    * **Home Assistant:** Docker Container `homeassistant`, Datenpfad `/home/pi/homeassistant`
    * **Pi-Nexus MCP Server:** Python Server unter `/home/pi/mcp-server/server.py`, Systemd `pi-nexus.service`, Port 8080 (intern) / via Cloudflare
    * **Cloudflare Tunnel (`pi-altlengbach`):** Systemd Service `cloudflared.service`, Config `/etc/cloudflared/config.yml`
      * `home.karl-mai.at` -> `http://127.0.0.1:8123` (Home Assistant Web-UI, extern verschlüsselt ohne Nabu Casa)
      * `mcp.karl-mai.at` -> `http://127.0.0.1:8080` (Pi-Nexus MCP Server Endpunkt)
    * **Automatisches SD-Boot-Backup:** `rpi-clone` auf `/dev/sda`
    * **Täglicher Health Check:** Cronjob 06:00 Uhr mit Push-Notification
  * Netzlaufwerk auf Windows: **`H:`** (`\\server\Klein-Schoderleh-Pi` via Rclone SFTP)
* **Synology NAS (`192.168.1.210`):**
  * Storage-Pool: 4 TB (~2,22 TB belegt, ~1,44 TB frei)
  * Netzlaufwerke auf Windows:
    * **`Y:`** = `\\192.168.1.210\home` (Admin-Verzeichnis: Backup, Drive, Phoniebox, Vincent Hochzeit)
    * **`O:`** = `\\192.168.1.210\Onedrive` (Onedrive Karl & Onedrive Lisa Archiv)
    * **`V:`** = `\\192.168.1.210\video` (27 Serien- und Mediathek-Ordner)
  * Weitere Freigaben: `homes`, `PlexMediaServer`, `photo`, `music`, `NetBackup`
  * Backup-Sync-Skript: `C:\Users\admin\AppData\Roaming\rclone\sync_pi_backups.ps1`
* **Samsung The Frame 43" (`192.168.1.26` / Wi-Fi Direct `192.168.137.247`):**
  * MAC: `d0:d0:03:a6:09:d2` (Samsung Electronics)
  * Verbunden als kabelloses Display via Miracast (Windows + K)

---

### B. Subnetz Gut Schoderleh & Hof (`172.17.0.0/24`)
* **Gut-Schoderleh-Pi (`172.17.0.154`):**
  * User: `pi` (Passwort: `raspberry`), SSH-Key `id_ed25519`
  * Services: Mosquitto MQTT Broker, Hof- und Stall-Steuerung
  * Netzlaufwerk auf Windows: **`I:`** (`\\server\Gut-Schoderleh-Pi` via Rclone SFTP)
* **Fronius Wechselrichter:**
  * Klein Schoderleh: `172.17.0.146`
  * Reithalle: `172.17.0.147`
  * Live eingebunden in Pi-Nexus MCP (`get_solar_stats`)

---

### C. Arbeits-Laptop (`BPA-Laptop-Karl`, `192.168.1.43`)
* **Hardware:** Intel Core i7-1355U (10 Kerne, 12 Threads), 16 GB RAM, 2 TB NVMe SSD
* **WLAN-Adapter:** Realtek RTL8852BE-VS WiFi 6 PCIe
* **Laufwerks-Zuordnungen:**
  * `C:` = Lokale SSD (Windows & Live-OneDrive)
  * `F:` = Retro-Fotobox (`\\100.119.165.12\Fotobox` via Tailscale)
  * `G:` = Google Drive (`G:\Meine Ablage\`)
  * `H:` = Klein-Schoderleh-Pi (`192.168.1.250`, Rclone SFTP)
  * `I:` = Gut-Schoderleh-Pi (`172.17.0.154`, Rclone SFTP)
  * `L:` = LetterboxStudio (`access-5021845669...`, Rclone SFTP)
  * `O:` = Synology OneDrive-Archiv (`\\192.168.1.210\Onedrive`, Windows SMB)
  * `R:` = Retro-Fotobox Webspace (`access-5021513742...`, Rclone SFTP)
  * `V:` = Synology Video (`\\192.168.1.210\video`, Windows SMB)
  * `Y:` = Synology Home (`\\192.168.1.210\home`, Windows SMB)
  * `Z:` = Fritz!NAS (`\\192.168.1.1\Mediaserver`, Windows SMB)
* **Hintergrund-Dienste & Wächter:**
  * **Rclone Autostart:** `shell:startup\Rclone_Drives.lnk` -> `mount_silent.vbs` -> `mount_drives.ps1` (läuft mit `WindowStyle Hidden` und `--no-console --links`)
  * **OneDrive Watchdog:** `onedrive_watchdog.vbs` -> `onedrive_watchdog.ps1` (prüft alle 15s auf Absturz und startet `OneDrive.exe /background` automatisch neu; Stop via `stop_onedrive_watchdog.cmd`)

---

## 2. Cloud- & DNS-Infrastruktur (Cloudflare)
* Alle 23 Domains bei World4You wurden auf Cloudflare DNS umgestellt.
* **Wichtigste Adressen:**
  * `https://home.karl-mai.at`: Externe SSL-Adresse für Home Assistant (Cloudflare Tunnel direkt auf Pi:8123)
  * `https://mcp.karl-mai.at/mcp`: MCP-Endpunkt für Antigravity und mobile Assistenten (Port 8080)
