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

def run_pipeline():
    print("--- X-iNet Multi-Format Generation inkl. Social ---")
    
    master = MasterTable()
    handler = SourceHandler()
    
    data_dir = os.path.join(BASE_DIR, "data")
    out_dir = os.path.join(BASE_DIR, "output")
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    
    # 1. Ranking & Quellen verarbeiten
    ranking_file = os.path.join(data_dir, "top_ranking.csv")
    if not os.path.exists(ranking_file):
        handler.download_ranking(ranking_file)
    master.load_ranking_list(ranking_file)
    
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

    # 2. Whitelist laden und anwenden
    whitelist_path = os.path.join(data_dir, "whitelist.txt")
    if os.path.exists(whitelist_path):
        with open(whitelist_path, "r") as f:
            whitelist = {line.strip().lower() for line in f if line.strip() and not line.startswith("#")}
            master.apply_whitelist(whitelist)
            print(f"✅ Whitelist angewendet ({len(whitelist)} Domains entfernt).")

    # 3. Daten fuer Multi-Export vorbereiten
    # Wir nehmen die Top 150.000 Domains basierend auf dem strategischen Ranking
    export_list = master.get_export_data(limit=150000)

    # 4. Multi-Format Export Engine
    print("Starte Multi-Format Export (10 Formate)...")
    
    formats = {
        "xinet_data.json": lambda d: json.dumps(d),
        "xinet_data.csv": lambda d: "domain,category\n" + "\n".join([f"{i['d']},{i['c']}" for i in d]),
        "xinet_universal_hosts.txt": lambda d: "\n".join([f"0.0.0.0 {i['d']}" for i in d]),
        "xinet_flint2.hosts": lambda d: "\n".join([i['d'] for i in d]), # Reine Domain-Liste
        "xinet_adguard.txt": lambda d: "\n".join([f"||{i['d']}^" for i in d]),
        "xinet_pihole.txt": lambda d: "\n".join([i['d'] for i in d]),
        "xinet_bind.rpz": lambda d: "\n".join([f"{i['d']} CNAME ." for i in d]),
        "xinet_mikrotik.rsc": lambda d: "/ip dns static\n" + "\n".join([f"add name={i['d']} address=0.0.0.0" for i in d]),
        "xinet_pfsense.conf": lambda d: "\n".join([f"local-zone: \"{i['d']}\" static" for i in d]),
        "xinet_unbound.conf": lambda d: "\n".join([f"local-data: \"{i['d']} A 0.0.0.0\"" for i in d])
    }

    for filename, formatter in formats.items():
        with open(os.path.join(out_dir, filename), "w") as f:
            f.write(formatter(export_list))
        print(f"  -> {filename} erstellt.")

    # 5. Status-Bericht
    master.generate_status_json(out_dir)
    print(f"--- FERTIG: Multi-Format Export abgeschlossen ---")

if __name__ == "__main__":
    run_pipeline()