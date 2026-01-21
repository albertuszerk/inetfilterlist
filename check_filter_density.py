import json
import os

# Pfad-Initialisierung
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_density_check():
    json_path = os.path.join(BASE_DIR, "output", "xinet_data.json")

    print("--- X-iNet Filter-Dichte-Check (Qualitaets-Analyse) ---")

    if not os.path.exists(json_path):
        print(f"❌ Export-Datei nicht gefunden: {json_path}")
        return

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Fehler beim Laden des JSON: {e}")
        return

    total = len(data)
    hits = 0
    categories_in_export = {}

    for entry in data:
        cat = entry.get('c', 'unknown')
        if cat != 'unknown':
            hits += 1
            categories_in_export[cat] = categories_in_export.get(cat, 0) + 1

    density = (hits / total) * 100 if total > 0 else 0

    print(f"Analysiere {total} exportierte Domains...")
    print(f"\nErgebnis:")
    print(f"  - Gefilterte Domains (Blocklist-Treffer): {hits}")
    print(f"  - Unbekannte Domains (Nur Ranking-Safe): {total - hits}")
    print(f"  - Filter-Dichte: {density:.2f}%")

    if hits > 0:
        print("\nKategorien-Verteilung im Export:")
        for cat, count in sorted(categories_in_export.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {cat}: {count} ({ (count/hits)*100:.1f}%)")
    else:
        print("\n⚠️ WARNUNG: Die Filter-Dichte ist 0%. Das Ranking ist zu dominant!")

    print("\n--- Analyse abgeschlossen ---")

if __name__ == "__main__":
    run_density_check()