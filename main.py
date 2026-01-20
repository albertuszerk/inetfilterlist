import yaml
import os
import json
import time
from datetime import datetime

# Importe
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

# --- KONFIGURATION DER LIMITS ---
LIMITS = {
    "mikrotik": 10000,
    "flint2": 50000,
    "fritzbox": 5000,
    "pihole": 100000,
    "hosts": 50000,
    "unbound": 25000,
    "dnsmasq": 25000,
    "rpz": 25000,
    "data": 100000 # JSON/CSV
}

def run_pipeline():
    print(f"--- X-iNet Multi-Format Generation ---")
    
    master_table = MasterTable()
    source_handler = SourceHandler(force_download=False)
    hierarchy_processor = HierarchyProcessor()
    
    with open("data/default_sources.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    r_handler = RankingHandler(config['ranking_sources'][0]['url'])
    global_ranks = r_handler.fetch_rankings()
    
    brutto_counter = 0
    for source in config['content_sources']:
        if not source.get('active', True): continue
        print(f"Verarbeite: {source['name']}...")
        domains = source_handler.fetch_tar_gz(source['url']) if source['adapter'] == "tar_gz_parser" else source_handler.fetch_plain_text(source['url'])
        brutto_counter += len(domains)
        for d in domains:
            master_table.add_domain(d, source['category'], global_ranks.get(d))
            
    # Veredelung
    all_raw = list(master_table.data.keys())
    unique_count = len(all_raw)
    clean_list = hierarchy_processor.clean_redundancies(all_raw)
    master_table.data = {d: master_table.data[d] for d in clean_list}
    
    # EXPORTE
    print("\nSchritt 4: Starte Multi-Format Export (10 Formate)...")
    categories = ['sex', 'violence', 'vpn_proxy', 'gambling']
    out = "output"
    
    # 1-3: Bereits bekannt
    MikrotikExporter(out).export(master_table.get_filtered_list(categories, limit=LIMITS["mikrotik"]), "xinet_mikrotik.rsc")
    FritzboxExporter(out).export(master_table.get_filtered_list(categories, limit=LIMITS["fritzbox"]), "xinet_fritzbox.txt")
    GlinetExporter(out).export(master_table.get_filtered_list(categories, limit=LIMITS["flint2"]), "xinet_flint2_adguard.txt")
    
    # 4-5: Universal
    univ = UniversalExporter(out)
    univ.export_hosts(master_table.get_filtered_list(categories, limit=LIMITS["hosts"]), "xinet_universal_hosts.txt")
    univ.export_pihole(master_table.get_filtered_list(categories, limit=LIMITS["pihole"]), "xinet_pihole.txt")
    
    # 6-8: Advanced
    adv = AdvancedExporter(out)
    adv.export_dnsmasq(master_table.get_filtered_list(categories, limit=LIMITS["dnsmasq"]), "xinet_dnsmasq.conf")
    adv.export_unbound(master_table.get_filtered_list(categories, limit=LIMITS["unbound"]), "xinet_unbound.conf")
    adv.export_rpz(master_table.get_filtered_list(categories, limit=LIMITS["rpz"]), "xinet_rpz.zone")
    
    # 9-10: Data
    dex = DataExporter(out)
    dex.export_json(master_table.get_filtered_list(categories, limit=LIMITS["data"]), "xinet_data.json")
    dex.export_csv(master_table.get_filtered_list(categories, limit=LIMITS["data"]), "xinet_data.csv")
    
    print(f"\n" + "="*45)
    print(f"   X-iNET MULTI-EXPORT STATUS")
    print(f"="*45)
    print(f"Netto-Datenbank:   {len(master_table.data):,}".replace(",", "."))
    print(f"Alle 10 Exporter erfolgreich abgeschlossen.")
    print(f"Dateien befinden sich im Ordner '/output'.")
    print(f"="*45)

if __name__ == "__main__":
    run_pipeline()