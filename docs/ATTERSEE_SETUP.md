# Home Assistant & Netzwerk-Infrastruktur – Attersee

Stand: 17.11.2026

---

## 1. Systemübersicht & Netzwerk

* **Standort & Provider:**
  * Provider: Cablevision Nöhmer GmbH (Schörfling am Attersee, Support: `+43 7662 3131` / `office@cn.at`).
  * WAN: Aktuell Carrier-Grade NAT (CGNAT) `100.64.149.245`, DNS: `185.27.121.36` / `185.27.120.43` (Mass Response Backbone).
  * Router / Netzwerk: TP-Link Omada SDN System mit Omada Gateway.
  * Fernwartung Netzwerk: TP-Link Omada Cloud (`omada.tplinkcloud.com`).

* **Knoten 1 – Raspberry Pi 4 (`172.17.0.250`):**
  * MAC: `88:A2:9E:9A:8C:69` (Kabelgebunden am Omada-Switch).
  * Betriebssystem: Raspberry Pi OS / Linux (User `pi`).
  * Home Assistant: Docker Container (Core 2024.10.4, Nabu Casa Cloud aktiv: `https://d4gkrta4ouco6rnkbqctz38m9cx32zt7.ui.nabu.casa`).
  * Omada Controller: Docker Container auf demselben Pi 4.
  * Mosquitto MQTT: Port 1883 auf `172.17.0.250`.
  * Hardware-Zubehör: Sonoff Zigbee 3.0 USB Dongle (`/dev/ttyUSB0`) für ZHA.
  * Stabilität: Läuft dauerhaft stabil (12+ Tage Uptime ohne Neustart).

* **Knoten 2 – Mini-PC (Intel):**
  * Frühere TeamViewer-ID: `1802150211` (nicht mehr erreichbar).
  * Status: Aktuell stromlos bzw. kein Netzwerk-Link im Omada Controller. Soll künftig außer Betrieb genommen oder autark neu aufgesetzt werden, da der Pi 4 alle Automatisierungen stabil bewältigt.

---

## 2. Backup & Konfigurations-Stand

* **Aktuelles Voll-Backup:**
  * Datei: `core_2024_10_4.tar` (105 MB)
  * Speicherort: `G:\Meine Ablage\Backup\core_2024_10_4.tar`
  * Inhalt: Vollständige Home Assistant Konfiguration, `.storage/`, Lovelace Dashboards, Automatisierungen und Custom Components (`goecharger`, `daikin_onecta`, `localtuya`, `nuki_ng`, `husqvarna_automower`, `reolink_dev`).
* **HACS-Status (Bekannter Bug):**
  * HACS ist deaktiviert mit `HacsDisabledReason.RESTORE`.
  * Ursache: Duplizierter Eintrag für `Joery/hass-afvalhulp` in `.storage/hacs.repositories` (Zeilen 43015 & 45352). Kann nach Erhalt der Host-Shell durch Bereinigung oder Löschen von `.storage/hacs.repositories` behoben werden.

---

## 3. Vor-Ort Checkliste (beim nächsten Besuch)

Sobald ein Laptop im lokalen Attersee-WLAN/LAN verbunden ist:

### Schritt 1: Shell-Zugang zum Pi 4
```bash
ssh pi@172.17.0.250
```

### Schritt 2: Tailscale installieren (Dauer: 1 Minute)
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```
*Nach der Autorisierung im Browser ist der Attersee-Pi dauerhaft im Tailnet `100.x.y.z` verfügbar – unabhängig von Provider, Router oder CGNAT.*

### Schritt 3: Cloudflare Tunnel einrichten (Dauer: 2 Minuten)
Einen `cloudflared`-Container neben Home Assistant und Omada starten:
```bash
docker run -d --name cloudflared --restart unless-stopped cloudflare/cloudflared:latest tunnel --no-autoupdate run --token <CLOUDFLARE_TUNNEL_TOKEN>
```
* Subdomain im Cloudflare Dashboard anlegen: z. B. `attersee.karl-mai.at` -> `http://172.17.0.250:8123` (inkl. WebSocket Support).
* In `configuration.yaml` von Home Assistant ergänzen:
  ```yaml
  http:
    use_x_forwarded_for: true
    trusted_proxies:
      - 172.16.0.0/12
      - 127.0.0.1
  ```

### Schritt 4: HACS-Cache bereinigen
```bash
rm -f /home/pi/homeassistant/.storage/hacs.repositories
docker restart homeassistant
```

### Schritt 5: Nabu Casa kündigen
Sobald `attersee.karl-mai.at` und Tailscale laufen, kann das Nabu-Casa-Abo final beendet werden.
