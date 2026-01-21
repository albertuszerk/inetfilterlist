import sys
import os
import json

# Pfad-Initialisierung
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    from core.master_table import MasterTable
    from adapters.source_handler import SourceHandler
except ImportError as e:
    print(f"❌ Fehler beim Laden der Module: {e}")
    sys.exit(1)

def load_whitelist(filepath):
    """Liest die Whitelist ein und gibt ein Set von Domains zurueck."""
    whitelist = set()
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                domain = line.strip().lower()
                if domain and not domain.startswith("#"):
                    whitelist.add(domain)
        print(f"✅ Whitelist geladen: {len(whitelist)} Ausnahmen gefunden.")
    else:
        print(f"⚠️ Keine Whitelist unter {filepath} gefunden.")
    return whitelist

def run_pipeline():
    print("--- X-iNet Multi-Format Generation inkl. Social ---")
    
    master = MasterTable()
    handler = SourceHandler()
    
    # Verzeichnisse sicherstellen
    data_dir = os.path.join(BASE_DIR, "data")
    out_dir = os.path.join(BASE_DIR, "output")
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    
    # 1. Ranking laden (Strategische Basis)
    ranking_file = os.path.join(data_dir, "top_ranking.csv")
    if not os.path.exists(ranking_file):
        handler.download_ranking(ranking_file)
    master.load_ranking_list(ranking_file)
    
    # 2. Quellen verarbeiten
    sources = [
        {"name": "UT1 Violence", "url": "https://dsi.ut-capitole.fr/blacklists/download/violence.tar.gz", "cat": "violence"},
        {"name": "UT1 Porn", "url": "https://dsi.ut-capitole.fr/blacklists/download/porn.tar.gz", "cat": "sex"},
        {"name": "UT1 Gambling", "url": "https://dsi.ut-capitole.fr/blacklists/download/gambling.tar.gz", "cat": "gambling"},
        {"name": "UT1 VPN", "url": "https://dsi.ut-capitole.fr/blacklists/download/vpn.tar.gz", "cat": "vpn_proxy"},
        {"name": "UT1 Social", "url": "https://dsi.ut-capitole.fr/blacklists/download/social_networks.tar.gz", "cat": "social"},
        {"name": "OISD Adult", "url": "https://nsfw.oisd.nl/domainswild2", "cat": "sex"},
        {"name": "OISD Ads", "url": "https://small.oisd.nl/domainswild2", "cat": "ads_tracking"}
    ]

    for s in sources:
        print(f"Verarbeite: {s['name']}...")
        try:
            domains = handler.fetch(s['url'])
            for d in domains:
                master.add_domain(d, s['cat'])
        except Exception as e:
            print(f"⚠️ Fehler bei {s['name']}: {e}")

    # 3. Whitelist anwenden (Bereinigung)
    whitelist_path = os.path.join(data_dir, "whitelist.txt")
    whitelist_domains = load_whitelist(whitelist_path)
    if whitelist_domains:
        master.apply_whitelist(whitelist_domains)

    # 4. Export (JSON fuer Webseite & Router)
    print("Erzeuge Web-Export (JSON) mit strategischem Boost...")
    export_data = master.get_export_data(limit=150000)
    
    json_output = os.path.join(out_dir, "xinet_data.json")
    with open(json_output, "w") as f:
        json.dump(export_data, f)
    print(f"✅ Export erfolgreich: {json_output}")

    # 5. Status-Bericht erzeugen
    master.generate_status_json(out_dir)
    
    print(f"--- FERTIG: {len(master.data)} Domains insgesamt in der DB ---")

if __name__ == "__main__":
    run_pipeline()