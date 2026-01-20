import yaml
import os
from core.normalizer import normalize_domain
from core.master_table import MasterTable
from core.hierarchy_processor import HierarchyProcessor
from adapters.source_handler import SourceHandler
from adapters.ranking_handler import RankingHandler
from exporters.mikrotik_exporter import MikrotikExporter

def load_whitelist(file_path):
    whitelist = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                normalized = normalize_domain(line)
                if normalized:
                    whitelist.add(normalized)
    return whitelist

def run_pipeline():
    print("--- X-iNet Filter Generation: Start ---")
    master_table = MasterTable()
    source_handler = SourceHandler()
    hierarchy_processor = HierarchyProcessor()
    
    config_path = "data/default_sources.yaml"
    whitelist_path = "data/whitelist.txt"
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    print("Lade Ranking-Daten...")
    ranking_cfg = config['ranking_sources'][0]
    r_handler = RankingHandler(ranking_cfg['url'])
    global_ranks = r_handler.fetch_rankings()
    
    for source in config['content_sources']:
        if not source.get('active', True): continue
        print(f"Verarbeite Quelle: {source['name']}...")
        if source['adapter'] == "tar_gz_parser":
            domains = source_handler.fetch_tar_gz(source['url'])
        else:
            domains = source_handler.fetch_plain_text(source['url'])
        print(f"  -> {len(domains)} Domains extrahiert.")
        for d in domains:
            master_table.add_domain(d, source['category'], global_ranks.get(d))
            
    print("Wende Whitelist an...")
    master_table.apply_whitelist(load_whitelist(whitelist_path))

    print("Starte Hierarchie-Pruefung...")
    all_raw = list(master_table.data.keys())
    clean_list = hierarchy_processor.clean_redundancies(all_raw)
    master_table.data = {d: master_table.data[d] for d in clean_list}
    
    # EXPORT-SEKTION
    print("Erstelle Export-Datei fuer MikroTik...")
    target_categories = ['sex', 'violence', 'vpn_proxy']
    export_list = master_table.get_filtered_list(target_categories, limit=5000)
    
    exporter = MikrotikExporter(output_dir="output")
    success_file = exporter.export(export_list, filename="xinet_blocklist.rsc")
    
    if success_file:
        print(f"ERFOLG: Datei erstellt unter {success_file}")
    
    print("\n--- Prozess abgeschlossen! ---")
    print(f"Netto-Eintraege in Master-Table: {len(master_table.data)}")
    print(f"Exportierte Domains: {len(export_list)}")

if __name__ == "__main__":
    run_pipeline()
