import json
import os
import sys

# Pfad-Initialisierung
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_integrity_check():
    json_path = os.path.join(BASE_DIR, "output", "xinet_data.json")
    status_path = os.path.join(BASE_DIR, "output", "status.json")

    print("--- X-iNet Pruefprotokoll (Integrations-Test) ---")

    # 1. Existenzpruefung
    if not os.path.exists(json_path):
        print(f"❌ FEHLER: Export-Datei {json_path} nicht gefunden.")
        return

    # 2. Daten laden
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ FEHLER beim Lesen des JSON: {e}")
        return

    # 3. Struktur-Pruefung
    print(f"✅ JSON erfolgreich geladen. Eintraege: {len(data)}")
    
    if isinstance(data, list):
        print("✅ Datenformat: Liste (korrekt fuer Router-Import)")
    else:
        print("⚠️ WARNUNG: Datenformat ist keine Liste.")

    # 4. Ranking-Validierung (Der strategische Check)
    print("\nCheck der Top-Prioritaeten (Ranking-Validierung):")
    top_check = data[:10]
    for i, entry in enumerate(top_check, 1):
        # Angepasst an die neue Struktur {'d': 'domain', 'c': 'category'}
        domain = entry.get('d', 'N/A')
        category = entry.get('c', 'unknown')
        print(f"  [{i}] {domain} (Kategorie: {category})")

    # 5. Dubletten-Check
    # Wir extrahieren nur die Domain-Namen ('d') fuer den Check
    domain_names = [entry.get('d') for entry in data if 'd' in entry]
    unique_domains = set(domain_names)
    
    if len(unique_domains) == len(data):
        print("\n✅ Keine Dubletten im Export gefunden.")
    else:
        diff = len(data) - len(unique_domains)
        print(f"\n⚠️ WARNUNG: {diff} Dubletten im Export gefunden!")

    # 6. Status-Abgleich
    if os.path.exists(status_path):
        with open(status_path, "r") as f:
            stats = json.load(f)
        print(f"\nStatistik-Abgleich:")
        print(f"  Gesamt-Datenbank: {stats.get('total_domains')} Domains")
        print(f"  Kategorien-Mix im Master:")
        for cat, count in stats.get("categories", {}).items():
            print(f"    - {cat}: {count}")
    
    print("\n--- Pruefung abgeschlossen ---")

if __name__ == "__main__":
    run_integrity_check()