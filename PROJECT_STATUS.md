# Home Assistant & Pi-Nexus Projekt-Status (Gut & Klein Schoderleh)

Stand: 16.11.2026, 13:45 Uhr

---

## 1. Systemübersicht & Netzwerk
Ausführliche technische Details zu allen Knoten, Subnetzen und Diensten siehe [docs/NETWORK_INFRASTRUCTURE.md](file:///C:/Repos/homeassistant/docs/NETWORK_INFRASTRUCTURE.md).

* **Klein-Schoderleh-Pi (`192.168.1.250`):**
  * OS: Raspberry Pi OS (User `pi`, SSH-Key `id_ed25519` / PW `raspberry`)
  * Home Assistant: Docker Container `homeassistant`, Config in `/home/pi/homeassistant`
  * Pi-Nexus MCP-Server: `/home/pi/mcp-server/server.py` (Port 8080 / via Cloudflare `https://mcp.karl-mai.at/mcp`)
  * Cloudflare Tunnel: `home.karl-mai.at` (Home Assistant Web-UI per SSL)
  * Fronius Wechselrichter: Live-Abfrage von `172.17.0.146` (Klein Schoderleh) und `172.17.0.147` (Reithalle)
* **Gut-Schoderleh-Pi (`172.17.0.154`):**
  * Mosquitto MQTT & Hof-Steuerung (SSH-Key `id_ed25519`)
* **Synology NAS (`192.168.1.210`):**
  * 4 TB Speicherpool mit Freigaben `home`, `Onedrive`, `video`, `homes`, `PlexMediaServer`, `photo`, `music`, `NetBackup`
* **Laufwerks-Zuordnung (Windows Host):**
  * `H:` = `Klein-Schoderleh-Pi` (`192.168.1.250`, Rclone SFTP via SSH-Key)
  * `I:` = `Gut-Schoderleh-Pi` (`172.17.0.154`, Rclone SFTP via SSH-Key)
  * `L:` = `LetterboxStudio` (Rclone SFTP)
  * `O:` = `\\192.168.1.210\Onedrive` (Synology Onedrive-Archiv)
  * `R:` = `Retro-Fotobox` (Rclone SFTP)
  * `V:` = `\\192.168.1.210\video` (Synology Video- & Mediathek)
  * `Y:` = `\\192.168.1.210\home` (Synology Admin-Home)
  * `Z:` = `\\192.168.1.1\Mediaserver` (Fritz!NAS USB 3.0)
  * Autostart: `shell:startup\Rclone_Drives.lnk` -> `mount_silent.vbs` (komplett fensterlos)

---

## 2. Aktueller Status Home Assistant
* **Integrationen:** Alle 102 Config-Entries & 2.280 Entities aktiv (HomematicIP, Tuya, Shelly, LocalTuya, Fritzbox, Sonos, Synology, Daikin, Hue etc.).
* **Backups:** Tägliche Backups in `/home/pi/homeassistant/backups/`.
* **Lokale Sicherungen:** In `/home/pi/homeassistant/` liegen `.bak_pumpfix`-Kopien von `automations.yaml`, `configuration.yaml` und `.storage/`.

---

## 3. Offene Aufgaben & Anforderungen
1. **Go-e Charger Einbindung:**
   * Neuer Go-e Charger wurde in Betrieb genommen und muss noch ins Zielnetzwerk eingebunden und in Home Assistant integriert werden.
2. **Dashboard- & Statistik-Monitoring:**
   * Langzeit-Plausibilität der Brunnen- und Pumpenstatistiken (LTS-Werte & Durchflussmengen) im Dashboard prüfen.
3. **Netzwerk-Automatisierungen:**
   * Weiterer Ausbau der Automationen über Pi-Nexus und MQTT.

---

## 4. Dokumentation & Historie
* [docs/NETWORK_INFRASTRUCTURE.md](file:///C:/Repos/homeassistant/docs/NETWORK_INFRASTRUCTURE.md) – Detaillierte Netzwerktopologie, IPs, Ports und Dienste
* [docs/ATTERSEE_SETUP.md](file:///C:/Repos/homeassistant/docs/ATTERSEE_SETUP.md) – Attersee Infrastruktur, Backup-Stand & Vor-Ort Checkliste
* [docs/CHAT_SESSION_TRANSFER.md](file:///C:/Repos/homeassistant/docs/CHAT_SESSION_TRANSFER.md) – Vollständiges Übergabeprotokoll aus der bisherigen Hauptsession
* [docs/onleihe_watcher_chat_backup.md](file:///C:/Repos/homeassistant/docs/onleihe_watcher_chat_backup.md) – Onleihe-Watcher Projektstand
