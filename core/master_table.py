import json
import os
from datetime import datetime
from core.normalizer import normalize_domain

class MasterTable:
    def __init__(self):
        self.data = {}
        self.default_rank = 1000000

    def load_ranking_list(self, filepath):
        if not os.path.exists(filepath):
            print(f"⚠️ Keine Ranking-Datei zum Einlesen gefunden.")
            return

        print(f"Initialisiere Ranking-Logik...")
        count = 0
        with open(filepath, "r") as f:
            for i, line in enumerate(f, 1):
                parts = line.strip().split(",")
                domain = parts[-1] 
                normalized = normalize_domain(domain)
                if normalized:
                    if normalized not in self.data:
                        self.data[normalized] = {"categories": set(), "rank": i}
                    else:
                        self.data[normalized]["rank"] = i
                    count += 1
        print(f"✅ {count} Domains wurden erfolgreich priorisiert.")

    def add_domain(self, domain, category, rank=None):
        if domain not in self.data:
            self.data[domain] = {
                "categories": {category},
                "rank": rank if rank is not None else self.default_rank
            }
        else:
            self.data[domain]["categories"].add(category)
            if rank is not None and rank < self.data[domain]["rank"]:
                self.data[domain]["rank"] = rank

    def generate_status_json(self, output_dir):
        stats = {
            "total_domains": len(self.data),
            "categories": {},
            "last_update": datetime.now().isoformat()
        }
        for info in self.data.values():
            for cat in info["categories"]:
                stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
        
        file_path = os.path.join(output_dir, "status.json")
        with open(file_path, "w") as f:
            json.dump(stats, f, indent=4)
        print(f"✅ Statusbericht unter {file_path} gespeichert.")