import sys
import os

# Pfad-Initialisierung
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    from core.master_table import MasterTable
    from adapters.source_handler import SourceHandler
    from exporters.data_exporter import DataExporter
except ImportError as e:
    print(f"❌ Fehler beim Laden der Module: {e}")
    sys.exit(1)

def run_pipeline():
    print("--- X-iNet Multi-Format Generation inkl. Social ---")
    
    master = MasterTable()
    # load_ranking() wurde entfernt, da die Funktion in MasterTable fehlt
    
    handler = SourceHandler()

    # Die vervollstaendigte Quellenliste inkl. Social
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
                # Wir schreiben die Domain mit ihrer Kategorie in die Master-Tabelle
                master.add_domain(d, s['cat'])
        except Exception as e:
            print(f"⚠️ Fehler bei {s['name']}: {e}")

    out = "output"
    if not os.path.exists(out): os.makedirs(out)

    print("Erzeuge Web-Export (JSON)...")
    exporter = DataExporter(out)
    # Hier werden die 150.000 wichtigsten Domains fuer die Webseite gespeichert
    exporter.export_web_json(master.data, "xinet_data.json", limit=150000)

    print("Erzeuge Status-Bericht...")
    master.generate_status_json(out)
    
    print(f"--- FERTIG: {len(master.data)} Domains verarbeitet ---")

if __name__ == "__main__":
    run_pipeline()