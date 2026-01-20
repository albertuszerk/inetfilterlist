import yaml
import os
import json
import time
from datetime import datetime

from core.normalizer import normalize_domain
from core.master_table import MasterTable
from core.hierarchy_processor import HierarchyProcessor
from adapters.source_handler import SourceHandler
from adapters.ranking_handler import RankingHandler
from exporters.mikrotik_exporter import MikrotikExporter
from exporters.fritzbox_exporter import FritzboxExporter
from exporters.glinet_exporter import GlinetExporter
from exporters.universal_exporter import UniversalExporter
from exporters.advanced_exporter import AdvancedExporter
from exporters.data_exporter import DataExporter

# --- KONFIGURATION ---
FORCE_REDOWNLOAD = False
EXPORT_LIMIT_DEFAULT = 10000
WEB_DATA_LIMIT = 150000 # Wie viele Domains darf die Webseite verarbeiten?

def run_pipeline():
    print(f"--- X-iNet Multi-Format Generation ---")
    
    master_table = MasterTable()
    source_handler = SourceHandler(force_download=FORCE_REDOWNLOAD)
    hierarchy_processor = HierarchyProcessor()
    
    with open("data/default_sources.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    r_handler = RankingHandler(config['ranking_sources'][0]['url'])
    global_ranks = r_handler.fetch_rankings()
    
    status_report = {"metadata": {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "brutto": 0}, "sources": []}
    
    for source in config['content_sources']:
        if not source.get('active', True): continue
        print(f"Verarbeite: {source['name']}...")
        domains = source_handler.fetch_tar_gz(source['url']) if source['adapter'] == "tar_gz_parser" else source_handler.fetch_plain_text(source['url'])
        status_report["metadata"]["brutto"] += len(domains)
        status_report["sources"].append({"name": source['name'], "category": source['category'], "count": len(domains), "status": "green" if len(domains) > 0 else "red"})
        for d in domains:
            master_table.add_domain(d, source['category'], global_ranks.get(d))
            
    # Veredelung
    all_raw = list(master_table.data.keys())
    clean_list = hierarchy_processor.clean_redundancies(all_raw)
    master_table.data = {d: master_table.data[d] for d in clean_list}
    status_report["metadata"]["netto"] = len(master_table.data)
    
    if not os.path.exists("output"): os.makedirs("output")
    with open("output/status.json", "w", encoding="utf-8") as f:
        json.dump(status_report, f, indent=4)
    
    # Exporte
    print("\nSchritt 4: Erzeuge Export-Dateien...")
    categories = ['sex', 'violence', 'vpn_proxy', 'gambling']
    out = "output"
    
    MikrotikExporter(out).export(master_table.get_filtered_list(categories, limit=10000), "xinet_mikrotik.rsc")
    FritzboxExporter(out).export(master_table.get_filtered_list(categories, limit=5000), "xinet_fritzbox.txt")
    GlinetExporter(out).export(master_table.get_filtered_list(categories, limit=50000), "xinet_flint2_adguard.txt")
    
    # Die neue Web-Schnittstelle
    DataExporter(out).export_web_json(master_table.data, "xinet_data.json", limit=WEB_DATA_LIMIT)
    
    print(f"--- FERTIG: {len(master_table.data)} Domains gesichert ---")

if __name__ == "__main__":
    run_pipeline()