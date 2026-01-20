
import requests
import zipfile
import io
import csv
from core.normalizer import normalize_domain

class RankingHandler:
    def __init__(self, url="https://tranco-list.eu/top-1m.csv.zip"):
        self.url = url
        self.timeout = 20

    def fetch_rankings(self):
        """
        Lädt die Top-1-Million-Liste herunter, entpackt sie im RAM
        und gibt ein Dictionary {domain: rank} zurück.
        """
        rank_lookup = {}
        try:
            print(f"Lade Ranking-Daten von {self.url}...")
            response = requests.get(self.url, timeout=self.timeout)
            
            if response.status_code == 200:
                # ZIP im Arbeitsspeicher öffnen
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    # Wir nehmen die erste CSV-Datei im Archiv
                    csv_filename = z.namelist()[0]
                    with z.open(csv_filename) as f:
                        # Stream-Reader für CSV
                        reader = csv.reader(io.TextIOWrapper(f, encoding='utf-8'))
                        for row in reader:
                            if len(row) >= 2:
                                rank = int(row[0])
                                raw_domain = row[1]
                                
                                # Auch die Ranking-Domains müssen normalisiert werden
                                # (ss-Regel, Kleinschreibung etc.)
                                domain = normalize_domain(raw_domain)
                                
                                if domain:
                                    rank_lookup[domain] = rank
            
            print(f"Ranking-Daten geladen: {len(rank_lookup)} Einträge.")
            return rank_lookup
            
        except Exception as e:
            print(f"Fehler beim Laden der Ranking-Daten: {e}")
            return {}

# Beispielhafte Nutzung im Hauptprogramm:
# r_handler = RankingHandler()
# global_ranks = r_handler.fetch_rankings()
# rank = global_ranks.get("beispiel.de", 1000001)
