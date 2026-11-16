# Home Assistant & Pi-Nexus Projekt-Status (Gut & Klein Schoderleh)

Stand: 15.11.2026, 23:12 Uhr

---

## 1. Systemübersicht & Netzwerk
- **Klein-Schoderleh-Pi (`192.168.1.250`):**
  - OS: Raspberry Pi OS (User `pi`, PW `raspberry`)
  - Home Assistant (Docker-Container `homeassistant`, Config in `/home/pi/homeassistant`)
  - Pi-Nexus MCP-Server (`/home/pi/mcp-server/server.py`, Systemd `pi-nexus.service`, Port 8000 / via Cloudflare `https://mcp.karl-mai.at/mcp`)
  - Tool `get_solar_stats` bindet beide Fronius-Wechselrichter live ein:
    - Klein-Schoderleh: `172.17.0.146`
    - Reithalle: `172.17.0.147`
- **Gut-Schoderleh-Pi (`172.17.0.154`):**
  - Mosquitto MQTT & Hof-Steuerung
- **Synology NAS (`192.168.1.210`):**
  - Reiner passiver Backup-Datenspeicher
- **Laufwerks-Zuordnung (Windows Host via Rclone & SSH-Key `id_ed25519`):**
  - `H:` = `Klein-Schoderleh-Pi` (`192.168.1.250`, `\\server\Klein-Schoderleh-Pi`)
  - `I:` = `Gut-Schoderleh-Pi` (`172.17.0.154`, `\\server\Gut-Schoderleh-Pi`)
  - `R:` = `Retro-Fotobox` (`access-5021513742...`, `\\server\Retro-Fotobox`)
  - `L:` = `LetterboxStudio` (`access-5021845669...`, `\\server\LetterboxStudio`)
  - `Y:` = `Netzwerkplatte` (Synology `\\192.168.1.210\home`)
  - `Z:` = `Fritz NAS` (`\\192.168.1.1\Mediaserver`)
  - **Autostart:** `mount_silent.vbs` in Windows-Startup ruft `mount_drives.ps1` komplett fensterlos auf (`-WindowStyle Hidden --no-console --links`).

---

## 2. Aktueller Status Home Assistant
- **Integrationen:** Alle 102 Config-Entries & 2.280 Entities aktiv (HomematicIP, Tuya, Shelly, LocalTuya, Fritzbox, Sonos, Synology, Daikin, Hue, etc.).
- **Tägliche Backups:** Liegen in `/home/pi/homeassistant/backups/`.
- **Lokale Sicherheitskopien:** In `/home/pi/homeassistant/` liegen `.bak_pumpfix`-Kopien von `automations.yaml`, `configuration.yaml` und `.storage/`.

---

## 3. Offene Aufgaben & Anforderungen Wasser/Pumpen
1. ~~**Schwimmerschalter 24V Alarm (`Shelly_i4_Schwimmer` / `binary_sensor.schalter_schwimmer_24v_input_0`):**~~ ✅ Erledigt (15.11.2026)
   - Trigger `on` für 60s, Condition `switch.pumpe_1` & `switch.pumpe_2` `off`, Push an Karl & Helmuth, 24h-Wiederholung via `wait_for_trigger`.
2. ~~**LTS (Long-Term Statistics > 14 Tage):**~~ ✅ Erledigt (15.11.2026)
   - Für Brunnen- und Durchflusssensoren `unit_of_measurement: "L"` und `state_class` in `configuration.yaml` (`homeassistant: customize:`) ergänzt.
3. ~~**Pumpenstatistik & Eventlog Minuten-Formatierung:**~~ ✅ Erledigt (15.11.2026)
   - `sensor.pumpe_1_letzte_pumpung` und `sensor.pumpe_2_letzte_pumpung` auf `round(1)` mit `this.state`-Neustartschutz korrigiert (`0.0 min` statt `e-06`).
4. **Go-e Charger Einbindung:**
   - Neuer Go-e Charger wurde in Betrieb genommen und muss noch ins Zielnetzwerk eingebunden werden.
