
import yaml
from adapters.source_handler import SourceHandler
from adapters.ranking_handler import RankingHandler
from core.master_table import MasterTable

def run_pipeline():
    print("--- X-iNet Filter Generation Start ---")
    
    # 1. Initialisierung
    master_table = MasterTable()
    source_handler = SourceHandler()
    
    # 2. Konfiguration laden
    with open("data/default_sources.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # 3. Ranking-Daten laden (Die Wichtigkeits-Skala)
    # Wir nehmen die erste Ranking-Quelle aus der Config
    ranking_cfg = config['ranking_sources'][0]
    r_handler = RankingHandler(ranking_cfg['url'])
    global_ranks = r_handler.fetch_rankings()
    
    # 4. Inhalts-Quellen abarbeiten (Saugpumpen aktivieren)
    for source in config['content_sources']:
        if not source.get('active', True):
            continue
            
        print(f"Verarbeite Quelle: {source['name']} ({source['category']})...")
        
        # Je nach Adapter-Typ die richtige Methode wählen
        if source['adapter'] == "tar_gz_parser":
            domains = source_handler.fetch_tar_gz(source['url'])
        else:
            domains = source_handler.fetch_plain_text(source['url'])
            
        # Daten in die Master-Table übertragen und mit Ranking verknüpfen
        for d in domains:
            rank = global_ranks.get(d) # Gibt Rank zurück oder None
            master_table.add_domain(d, source['category'], rank)
            
    # 5. Whitelist anwenden (Vermeidung von False-Positives)
    # TODO: Hier laden wir später die data/whitelist.txt
    
    # 6. Erste Erfolgsmeldung
    total_count = len(master_table.data)
    print(f"--- Prozess abgeschlossen! ---")
    print(f"Master-Table enthält jetzt {total_count} einzigartige Domains.")
    
    # 7. Test-Export (Nur zum Beweis, dass es funktioniert)
    # Wir exportieren die Top 10 der Kategorie 'sex'
    top_sex = master_table.get_filtered_list(['sex'], limit=10)
    print(f"Vorschau Top 10 Sex-Filter: {top_sex}")

if __name__ == "__main__":
    run_pipeline()
