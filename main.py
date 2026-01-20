import yaml
import os
from adapters.source_handler import SourceHandler
from adapters.ranking_handler import RankingHandler
from core.master_table import MasterTable
from core.hierarchy_processor import HierarchyProcessor
from core.normalizer import normalize_domain

def load_whitelist(file_path):
    """Lädt die Whitelist-Datei und normalisiert die Einträge."""
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
    # Wir nehmen die erste Ranking-Quelle aus der Konfiguration
    ranking_cfg = config['ranking_sources'][0]
    r_handler = RankingHandler(ranking_cfg['url'])
    global_ranks = r_handler.fetch_rankings()
    
    # 4. Inhalts-Quellen abarbeiten (Saugpumpen aktivieren)
    for source in config['content_sources']:
        if not source.get('active', True):
            print(f"Überspringe inaktive Quelle: {source['name']}")
            continue
            
        print(f"Verarbeite Quelle: {source['name']} (Kategorie: {source['category']})...")
        
        # Den richtigen Adapter basierend auf der Konfiguration wählen
        if source['adapter'] == "tar_gz_parser":
            domains = source_handler.fetch_tar_gz(source['url'])
        else:
            domains = source_handler.fetch_plain_text(source['url'])
            
        print(f"  -> {len(domains)} Domains gefunden.")
        
        # Daten in die Master-Table übertragen und mit Ranking verknüpfen
        for d in domains:
            rank = global_ranks.get(d) # Gibt den Platz zurück oder None
            master_table.add_domain(d, source['category'], rank)
            
    # 5. Whitelist anwenden (Die Sicherheits-Reissleine)
    print("Wende Whitelist an...")
    whitelist = load_whitelist(whitelist_path)
    master_table.apply_whitelist(whitelist)
    print(f"  -> {len(whitelist)} Domains dauerhaft zugelassen (Whitelist).")

    # 6. Veredelung: Hierarchie-Prüfung (Redundanz-Check)
    print("Starte Hierarchie-Prüfung (Entferne unnötige Subdomains)...")
    all_raw_domains = list(master_table.data.keys())
    clean_domains_list = hierarchy_processor.clean_redundancies(all_raw_domains)
    
    # Die Master-Table bereinigen: Wir behalten nur die 'clean' Domains
    original_count = len(master_table.data)
    redundant_count = original_count - len(clean_domains_list)
    
    # Temporäre Kopie der Daten, um nur die sauberen zu behalten
    cleaned_data = {d: master_table.data[d] for d in clean_domains_list}
    master_table.data = cleaned_data
    
    # 7. Abschluss-Statistik
    print("\n--- Prozess abgeschlossen! ---")
    print(f"Brutto-Domains gesammelt:  {original_count}")
    print(f"Redundante Subdomains entfernt: {redundant_count}")
    print(f"Netto-Einträge in Master-Table: {len(master_table.data)}")
    
    # 8. Test-Vorschau (Die Top 5 der wichtigsten gesperrten Seiten)
    # Dies hilft zu prüfen, ob das Ranking funktioniert
    preview = master_table.get_filtered_list(['sex', 'violence', 'vpn_proxy'], limit=5)
    print(f"\nVorschau der Top 5 wichtigsten Sperren:\n{preview}")

if __name__ == "__main__":
    run_pipeline()
