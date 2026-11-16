#!/usr/bin/env python3
"""Überwacht die Onleihe-3.0-Neuzugänge für noe-book.onleihe.com und meldet neue Titel an Home Assistant."""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ONLEIHE_ID = "696653369d468a92eb935de6"
LIBRARY_ID = "696653369d468a92eb935de8"
LOGIN_URL = "https://api.onleihe.de/user-application/v1/auth/login"
EXPLORE_URL = (
    f"https://api.onleihe.de/ui/v1/onleihe/{ONLEIHE_ID}/explore"
    f"?libraryId={LIBRARY_ID}&legacy=false"
)
CATALOG_URL = "https://noe-book.onleihe.com/search?exploreList=2"

MEDIA_TYPE_LABELS = {
    "E_BOOK": "E-Book",
    "E_AUDIO": "Hörbuch",
    "E_VIDEO": "Video",
    "E_MUSIC": "Musik",
}


def http_json(url: str, payload: dict | None = None, token: str | None = None) -> dict:
    """Führt einen HTTP-JSON-Request aus und gibt das geparste Ergebnis zurück."""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw.strip() else {}


def fetch_new_arrivals() -> list[dict]:
    """Holt die aktuelle Neuzugänge-Liste über einen anonymen Guest-Token."""
    auth = http_json(LOGIN_URL, payload={"onleiheId": ONLEIHE_ID, "libraryId": LIBRARY_ID})
    token = auth["accessToken"]
    explore = http_json(EXPLORE_URL, token=token)

    section = next(
        (el for el in explore.get("exploreElements", []) if el.get("title") == "Neuzugänge"),
        None,
    )
    if not section:
        raise RuntimeError("Abschnitt 'Neuzugänge' in der Onleihe-API nicht gefunden.")

    items = []
    for entry in section.get("products", []):
        prod = entry.get("product") or {}
        prod_id = entry.get("productId") or prod.get("id")
        if not prod_id:
            continue

        authors = [
            f"{a.get('firstName', '')} {a.get('lastName', '')}".strip()
            for a in prod.get("authors", [])
        ]
        author_str = ", ".join(a for a in authors if a)
        media_type = prod.get("mediaType", "")

        items.append(
            {
                "id": prod_id,
                "title": prod.get("title", "Unbekannter Titel"),
                "author": author_str,
                "media_type": media_type,
                "media_label": MEDIA_TYPE_LABELS.get(media_type, media_type or "Unbekannt"),
            }
        )
    return items


def load_seen_ids(state_file: Path) -> set[str] | None:
    """Lädt bereits gemeldete Produkt-IDs oder gibt None zurück, falls noch kein State existiert."""
    if not state_file.exists():
        return None
    data = json.loads(state_file.read_text(encoding="utf-8"))
    return set(data.get("seen_ids", []))


def save_seen_ids(state_file: Path, seen_ids: set[str]) -> None:
    """Speichert bekannte Produkt-IDs atomar in der State-Datei."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = state_file.with_suffix(".tmp")
    tmp_file.write_text(
        json.dumps({"seen_ids": sorted(seen_ids)}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp_file.replace(state_file)


def format_notification(new_items: list[dict]) -> dict:
    """Erstellt Titel und kompakten Nachrichtentext für die Home-Assistant-Benachrichtigung."""
    count = len(new_items)
    title = (
        f"Onleihe: {count} neues Buch" if count == 1 else f"Onleihe: {count} neue Bücher"
    )
    counts: dict[str, int] = {}
    for item in new_items:
        label = item["media_label"]
        counts[label] = counts.get(label, 0) + 1

    parts = []
    for label, n in counts.items():
        if label == "E-Book":
            parts.append(f"{n} E-Book" if n == 1 else f"{n} E-Books")
        elif label == "Hörbuch":
            parts.append(f"{n} Hörbuch" if n == 1 else f"{n} Hörbücher")
        else:
            parts.append(f"{n}× {label}")

    summary = ", ".join(parts)
    message = f"{summary} neu in der Onleihe verfügbar."

    return {
        "title": title,
        "message": message,
        "count": count,
        "url": CATALOG_URL,
        "items": new_items,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Onleihe 3.0 Neuzugänge-Watcher")
    parser.add_argument(
        "--state-file",
        type=Path,
        default=Path(__file__).with_name("seen_books.json"),
        help="Pfad zur JSON-Datei für bereits bekannte Buch-IDs",
    )
    parser.add_argument(
        "--webhook-url",
        default="",
        help="Home-Assistant-Webhook-URL (z. B. http://homeassistant.local:8123/api/webhook/onleihe_neue_buecher)",
    )
    parser.add_argument(
        "--notify-on-init",
        action="store_true",
        help="Auch beim allerersten Lauf (ohne seen_books.json) eine Benachrichtigung senden",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur ausgeben, keine State-Datei schreiben und keinen Webhook senden",
    )
    args = parser.parse_args()

    items = fetch_new_arrivals()
    current_ids = {item["id"] for item in items}
    seen_ids = load_seen_ids(args.state_file)

    if seen_ids is None:
        if not args.dry_run:
            save_seen_ids(args.state_file, current_ids)
        if not args.notify_on_init:
            print(f"Initialisiert mit {len(current_ids)} aktuellen Titeln.")
            return 0
        new_items = items
    else:
        new_items = [item for item in items if item["id"] not in seen_ids]

    if not new_items:
        print("Keine neuen Titel.")
        return 0

    payload = format_notification(new_items)
    print(f"{payload['title']}\n{payload['message']}")

    if args.dry_run:
        return 0

    if args.webhook_url:
        http_json(args.webhook_url, payload=payload)

    save_seen_ids(args.state_file, seen_ids | current_ids if seen_ids else current_ids)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (urllib.error.URLError, KeyError, RuntimeError) as exc:
        print(f"Fehler beim Onleihe-Check: {exc}", file=sys.stderr)
        sys.exit(1)
