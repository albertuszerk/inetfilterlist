import yaml
import os

# Importe unserer eigenen Module
from core.normalizer import normalize_domain
from core.master_table import MasterTable
from core.hierarchy_processor import HierarchyProcessor
from adapters.source_handler import SourceHandler
from adapters.ranking_handler import RankingHandler
from exporters.mikrotik_exporter import MikrotikExporter

def load_whitelist(file_path):
    """Laedt die Whitelist-Datei und normalisiert die Eintraege."""
    whitelist = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith(('#', '//')):
                    normalized = normalize_domain(line)
                    if normalized:
                        whitelist.add(normalized)
    return whitelist

def run_pipeline():
    print("--- X-iNet Filter Generation: Start ---")
    
    # 1. Initialisierung der Komponenten
    master_table = MasterTable()
    source_handler = SourceHandler()
    hierarchy_processor = HierarchyProcessor()
    
    # Pfade definieren
    config_path = "data/default_sources.yaml"
    whitelist_path = "data/whitelist.txt"
    
    # 2. Konfiguration laden
    if not os.path.exists(config_path):
        print(f"Fehler: Konfigurationsdatei {config_path} nicht gefunden!")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # 3. Ranking-Daten laden (Die Wichtigkeits-Skala)
    ranking_cfg = config['ranking_sources'][0]
    r_handler = RankingHandler(ranking_cfg['url'])
    global_ranks = r_handler.fetch_rankings()
    
    # 4. Inhalts-Quellen abarbeiten (Saugpumpen aktivieren)
    for source in config['content_sources']:
        if not source.get('active', True):
            print(f"Ueberspringe inaktive Quelle: {source['name']}")
            continue
            
        print(f"Verarbeite Quelle: {source['name']} (Kategorie: {source['category']})...")
        
        # Den richtigen Adapter basierend auf der Konfiguration waehlen
        if source['adapter'] == "tar_gz_parser":
            domains = source_handler.fetch_tar_gz(source['url'])
        else:
            domains = source_handler.fetch_plain_text(source['url'])
            
        print(f"  -> {len(domains)} Domains gefunden.")
        
        # Daten in die Master-Table uebertragen und mit Ranking verknuepfen
        for d in domains:
            rank = global_ranks.get(d) # Gibt den Platz zurueck oder None
            master_table.add_domain(d, source['category'], rank)
            
    # 5. Whitelist anwenden (Die Sicherheits-Reissleine)
    print("Wende Whitelist an...")
    whitelist = load_whitelist(whitelist_path)
    master_table.apply_whitelist(whitelist)
    print(f"  -> {len(whitelist)} Domains dauerhaft zugelassen (Whitelist).")

    # 6. Veredelung: Hierarchie-Pruefung (Redundanz-Check)
    print("Starte Hierarchie-Pruefung (Entferne unnoetige Subdomains)...")
    all_raw_domains = list(master_table.data.keys())
    clean_domains_list = hierarchy_processor.clean_redundancies(all_raw_domains)
    
    # Die Master-Table bereinigen: Wir behalten nur die 'clean' Domains
    original_count = len(master_table.data)
    redundant_count = original_count - len(clean_domains_list)
    
    cleaned_data = {d: master_table.data[d] for d in clean_domains_list}
    master_table.data = cleaned_data
    
    # 7. Der eigentliche Export fuer den Router
    print("Erstelle Export-Datei fuer MikroTik...")
    # Hier legen wir fest, welche Kategorien und welches Limit wir wollen
    # Fuer den ersten Test nehmen wir die Top 5000 der gewaehlten Kategorien
    target_categories = ['sex', 'violence', 'vpn_proxy']
    export_list = master_table.get_filtered_list(target_categories, limit=5000)
    
    exporter = MikrotikExporter(output_dir="output")
    exporter.export(export_list, filename="xinet_blocklist.rsc")
    
    # 8. Abschluss-Statistik
    print("\n--- Prozess abgeschlossen! ---")
    print(f"Brutto-Domains gesammelt:       {original_count}")
    print(f"Redundante Subdomains entfernt: {redundant_count}")
    print(f"Netto-Eintraege in Master-Table: {len(master_table.data)}")
    print(f"Exportierte Domains (Limiter):  {len(export_list)}")
    print(f"Datei wurde im Ordner 'output' gespeichert.")

if __name__ == "__main__":
    run_pipeline()
