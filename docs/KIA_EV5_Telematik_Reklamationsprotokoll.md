# Reklamations- & Fehlerprotokoll: KIA EV5 – Ausfälle der Telematik-Einheit (Kia Connect / CCU-Modem)

**Fahrzeug:** KIA EV5  
**FIN:** `KNAH481E6T7035652`  
**Erstellt am:** 20.11.2026  
**Beobachtungszeitraum:** 17.11.2026 – 20.11.2026  

---

## Fehlerbeschreibung (Kurzfassung für die Werkstatt)
Die eingebaute Telematik-Einheit (CCU / Mobilfunk-Modem, ccNC-System) verliert nach Standzeiten bzw. nach Beendigung eines Ladevorgangs regelmäßig und reproduzierbar die Datenverbindung zum Kia-Connect-Server („Zombie-Zustand“):
* Sowohl die **offizielle Kia Connect Smartphone-App** als auch die **Kia EU Connect API** zeigen über viele Stunden eingefrorene Alt-Werte (Batteriestand, Kilometerstand, Fahrzeugstatus).
* **Selbst während aktiver Fahrten im vollen Mobilfunknetz** sendet das Fahrzeug keine Status-Updates an den Kia-Server.
* Lokale Bluetooth-/UWB-Funktionen (z. B. Remote-Ein-/Ausparken direkt am Fahrzeug) funktionieren währenddessen normal – ausschließlich die Mobilfunk-Telematik (CCU) hängt.
* Auf aktive Weckrufe vom Kia-Backend reagiert das Fahrzeug in diesem Zustand nicht mehr; erst ein manueller Reset im Fahrzeug (*Kia Connect → Neu konfigurieren* bzw. Head-Unit-Reset) stellt die Verbindung vorübergehend wieder her.
* Die **12V-Starterbatterie** war durchgehend gut geladen (`82 % – 98 %`), eine Unterspannung als Ursache ist ausgeschlossen.

---

## Dokumentierte Einzelfälle (mit exakten Zeitstempeln)

| Nr. | Ausfallzeitraum (Lokalzeit MEZ) | Dauer ohne Kontakt | Eingefrorener Stand (App & Server) | Was tatsächlich passiert ist / Beleg | Behebung / Wiederanlauf |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **18.11.2026**<br>`08:07:38` → `20:23:39` | **12 Std. 16 Min.** | `73 %` SoC<br>`100,9 km` | Mehrere Fahrten im guten Mobilfunknetz (**+38,3 km** auf `139,2 km`, Verbrauch auf `61,5 %`). Remote-Parken vor Ort ging (BT), App & Server blieben auf `73 %`. Aktiver API-Weckruf (`GET /ccs2/carstatus`, `resCode: 0000`) blieb unbeantwortet. | Manuelles **„Kia Connect → Neu konfigurieren“** im Fahrzeug um `20:23 Uhr` → sofortige Meldung (`61,5 %`, `139,2 km`). |
| **2** | **20.11.2026**<br>ab `02:32:35` → laufend (`12:42+`) | **> 10 Std.** *(laufend)* | `100 %` SoC<br>`260,6 km` | Während der Nachtladung bis `02:32 Uhr` alle 30 Min. gemeldet. Direkt nach Ladeende (`100 %`, 12V-Batterie `98 %`) erneut eingefroren. **Vormittags bereits gefahren**, App zeigt trotzdem weiterhin `100 %` von `02:32 Uhr`. | Steht noch aus (Reset / Werkstatt-Prüfung). |

*(Hinweis: Am `19.11.2026` zwischen `12:08` und `18:00 Uhr` gab es ebenfalls eine 5h51m-Lücke (`206,0 km` → `228,4 km`), dort stand das Fahrzeug jedoch regulär geparkt und meldete sich um `18:00 Uhr` selbstständig wieder – dies war daher kein bestätigter Modem-Absturz. Am `19.11.` um `07:15:10 Uhr` schlug zudem eine geplante Vorklimatisierung mit Timeout zum Kia-EU-Server `prd.eu-ccapi.kia.com:8080` fehl.)*

---

## Erwartete Maßnahme durch den Kia-Händler / Werkstatt
1. Fehlerspeicher der **CCU (Central Communication Unit / Telematik-Steuergerät)** und des **ccNC-Infotainmentsystems** auslesen.
2. Prüfung auf verfügbare **Software-/Firmware-Updates bzw. Technische Service Bulletins (TSB)** für das ccNC-/CCU-Modem (bekannter Mobilfunk-Handshake-/Sleep-Bug bei neueren Kia-Modellen).
3. Falls Softwarestand aktuell ist und das Einfrieren weiterhin auftritt: Prüfung/Tausch der **Telematik-Einheit (CCU)** im Rahmen der Herstellergarantie.
