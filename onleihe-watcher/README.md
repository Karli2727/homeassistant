# Onleihe 3.0 Watcher (`noe-book.onleihe.com`)

Überwacht stündlich die Neuzugänge auf `noe-book.onleihe.com` ohne Login und ohne KI-Tokens.

## 1. Skript auf dem Raspberry Pi testen
```bash
python3 onleihe_watcher.py --dry-run --notify-on-init
```
Erster produktiver Lauf (speichert den aktuellen Stand in `seen_books.json` ohne Benachrichtigung):
```bash
python3 onleihe_watcher.py
```

## 2. Home Assistant Automation einrichten
1. In Home Assistant unter **Einstellungen → Automatisierungen & Szenen → Neue Automatisierung** oben rechts auf **Als YAML bearbeiten** wechseln.
2. Inhalt aus `ha_automation.yaml` einfügen und `notify.mobile_app_DEIN_HANDY` durch deinen echten Notify-Dienst ersetzen (z. B. `notify.mobile_app_karls_iphone`).

## 3. Stündlichen Cronjob auf dem Pi anlegen
`crontab -e` öffnen und folgende Zeile ergänzen (läuft immer zur Minute 5):
```cron
5 * * * * /usr/bin/python3 /home/pi/onleihe-watcher/onleihe_watcher.py --webhook-url http://127.0.0.1:8123/api/webhook/onleihe_neue_buecher >> /home/pi/onleihe-watcher/watcher.log 2>&1
```
*(Falls Home Assistant auf einem anderen Host/Port läuft, `127.0.0.1:8123` entsprechend anpassen.)*
