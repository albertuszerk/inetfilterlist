import json
import os
from datetime import datetime
from core.normalizer import normalize_domain

class MasterTable:
    def __init__(self):
        # Struktur: { "domain.com": {"categories": set(), "rank": 1000000} }
        self.data = {}
        self.default_rank = 1000000 
        self.filter_boost = 950000 # Erhoeht die Prioritaet von Filter-Treffern

    def load_ranking_list(self, filepath):
        if not os.path.exists(filepath):
            print(f"⚠️ Keine Ranking-Datei gefunden.")
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
        """Fuegt Domain hinzu und wendet den strategischen Filter-Boost an."""
        if domain not in self.data:
            # Neue Domain aus einer Filterliste erhaelt sofort einen besseren Rang
            adjusted_rank = self.default_rank - self.filter_boost
            self.data[domain] = {
                "categories": {category},
                "rank": adjusted_rank
            }
        else:
            # Bestehende Domain (z.B. google.com) wird markiert und aufgewertet
            self.data[domain]["categories"].add(category)
            if category != 'unknown':
                # Boost anwenden: Rang verbessern (verkleinern)
                current_rank = self.data[domain]["rank"]
                self.data[domain]["rank"] = max(1, current_rank - self.filter_boost)

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

    def get_export_data(self, limit=150000):
        """Liefert die Top-Domains sortiert nach dem geboosteten Rang."""
        # Umwandeln in Liste fuer Sortierung
        export_list = []
        for domain, info in self.data.items():
            # Wir nehmen nur Domains, die mindestens eine echte Kategorie haben
            # oder sehr wichtig im Ranking sind.
            cat_list = list(info["categories"])
            primary_cat = cat_list[0] if cat_list else "unknown"
            
            export_list.append({
                "d": domain,
                "c": primary_cat,
                "r": info["rank"]
            })

        # Sortieren: Niedrigster Rang zuerst
        export_list.sort(key=lambda x: x["r"])
        
        # Nur d und c fuer den Export behalten
        return [{"d": item["d"], "c": item["c"]} for item in export_list[:limit]]