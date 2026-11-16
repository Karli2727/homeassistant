# Vollständiges Übergabeprotokoll aus der Haupt-Session

Datum: 15.11.2026 – 16.11.2026

---

## 1. Ausgangslage & Zielsetzung
In der vorherigen Hauptsession wurden umfangreiche Arbeiten an der Infrastruktur von Gut und Klein Schoderleh vorgenommen. Alle relevanten Daten und der technische Kontext werden hiermit in das Projekt `C:\Repos\homeassistant` übergeben, damit dort nahtlos an Netzwerk, Sensoren, Pumpen und Automatisierungen weitergearbeitet werden kann.

---

## 2. Erledigte Arbeiten im Detail

### 1. Home Assistant Stabilität & Wiederherstellung
* **Problem:** Beim Bearbeiten von Template-Sensoren geriet Home Assistant kurzzeitig in einen Fallback-Modus (nur 4 Integrationen aktiv).
* **Lösung:** 
  * Docker-Container `homeassistant` sauber gestoppt.
  * 1:1 Wiederherstellung aus `.bak_pumpfix`: `core.config_entries` (102 Einträge) und `core.entity_registry` (2.280 Entities).
  * Berechtigungen auf `pi:pi` korrigiert, Container neu gestartet.
  * **Ergebnis:** Alle 102 Integrationen (HomematicIP, Tuya, Shelly, LocalTuya, Fritzbox, Sonos, Synology, Daikin, Hue etc.) laufen zu 100 % fehlerfrei.

### 2. Wasser- & Pumpen-Anforderungen (Klein Schoderleh)
* **Schwimmerschalter 24V Alarm:**
  * Entity: `Shelly_i4_Schwimmer` / `binary_sensor.schalter_schwimmer_24v_input_0`
  * Logik: Wenn Schalter länger als 60s `on` ist und `switch.pumpe_1` sowie `switch.pumpe_2` `off` sind $\rightarrow$ Push-Alarmierung an Karl & Helmuth, Wiederholung alle 24h solange der Zustand anhält.
* **LTS (Long-Term Statistics > 14 Tage):**
  * In `/home/pi/homeassistant/configuration.yaml` unter `homeassistant: customize:` für Brunnen- und Durchflusssensoren `unit_of_measurement: "L"` und `state_class: total_increasing` hinterlegt.
* **Pumpenstatistik & Eventlog Minuten-Formatierung:**
  * Sensoren `sensor.pumpe_1_letzte_pumpung` und `sensor.pumpe_2_letzte_pumpung` auf `round(1)` mit `this.state`-Neustartschutz korrigiert (verhindert kryptische Fließkommazahlen wie `0.000004 min` bzw. `e-06`).

### 3. Cloudflare & Fernzugriff
* **Cloudflare Tunnel (`pi-altlengbach`):**
  * Eingerichtet auf `192.168.1.250`.
  * `home.karl-mai.at` leitet direkt und per SSL verschlüsselt auf Port 8123 (Home Assistant). Nabu Casa (~75 €/Jahr) ist damit nicht mehr zwingend erforderlich.
  * `mcp.karl-mai.at` leitet auf den Pi-Nexus MCP-Server (Port 8080).
* **23 Domains bei World4You:**
  * Nameserver für alle 23 Domains auf Cloudflare-Nameserver umgestellt, um Schutz, globale DNS-Verwaltung und flexible Tunnels zu ermöglichen.

### 4. Pi-Nexus MCP-Server
* Läuft auf `192.168.1.250` als Systemd-Service `pi-nexus.service` (`/home/pi/mcp-server/server.py`).
* Stellt 11 Werkzeuge bereit (Systemstats, Backup-Status, Health-Checks, Shared Notes, Home Assistant Entity-Abfrage & Dienstaufrufe).
* Tool `get_solar_stats` liest beide Fronius-Wechselrichter (`172.17.0.146` und `172.17.0.147`) live per REST-API aus.

### 5. Windows Netzlaufwerke & Rclone
* SSH-Authentifizierung auf beiden Pis (`192.168.1.250` und `172.17.0.154`) auf Public Key (`id_ed25519`) umgestellt.
* Rclone-Mounts für `H:`, `I:`, `L:`, `R:` in `mount_drives.ps1` komplett lautlos und fensterlos konfiguriert (`Start-Process -WindowStyle Hidden` mit `--no-console --links --network-mode`).
* Windows Startup Verknüpfung `Rclone_Drives.lnk` ruft `mount_silent.vbs` auf $\rightarrow$ automatische Bereitstellung bei jedem PC-Start ohne Konsolenfenster.
* Synology-Freigaben dauerhaft eingebunden:
  * `O:` = `\\192.168.1.210\Onedrive`
  * `V:` = `\\192.168.1.210\video`
  * `Y:` = `\\192.168.1.210\home`

### 6. OneDrive-Migration & Watchdog
* Lokaler Download von ~300 GB auf `C:\Users\admin\OneDrive` läuft (bereits >185 GB geladen).
* Downloadrate in OneDrive auf 20.000 KB/s gedrosselt, um Hitze und Abstürze zu minimieren.
* Automatischer Wächter `onedrive_watchdog.ps1` aktiv: Prüft alle 15s im Hintergrund und startet `OneDrive.exe /background` automatisch neu, falls es wegen Pufferüberlauf abstürzt.

### 7. Display-Verbindung (Samsung The Frame 43")
* Diagnose für die 5-Minuten-Freezes bei `Windows + K` (Miracast):
  * Ursache: Kollision auf dem Realtek RTL8852BE WLAN-Chip zwischen heavy OneDrive-Download und Wi-Fi Direct H.264 Videostream.
  * Empfehlung: Drosselung/Pause während Präsentationen oder dauerhafte Verbindung per USB-C/HDMI-Kabel (für echte 4K@60Hz Schärfe und null Latenz).

---

## 3. Offene Punkte für das Projekt `homeassistant`
1. **Go-e Charger Einbindung:**
   * Neuer Go-e Charger wurde physisch in Betrieb genommen und muss noch ins Zielnetzwerk eingebunden und in Home Assistant integriert werden.
2. **Dashboard-Feinschliff & Automationen:**
   * Überprüfung der Pumpenstatistiken im Produktivbetrieb (letzte Pumpung, Betriebsstunden, Fördermengen).
3. **Netzwerküberwachung & Monitoring:**
   * Ausbau von Pi-Nexus und HA-Automationen für Hof & Haus.
