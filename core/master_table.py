import json
import os
from datetime import datetime
from core.normalizer import normalize_domain

class MasterTable:
    def __init__(self):
        self.data = {}
        self.default_rank = 1000000 
        self.filter_boost = 950000 

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
        if domain not in self.data:
            adjusted_rank = self.default_rank - self.filter_boost
            self.data[domain] = {"categories": {category}, "rank": adjusted_rank}
        else:
            self.data[domain]["categories"].add(category)
            if category != 'unknown':
                current_rank = self.data[domain]["rank"]
                self.data[domain]["rank"] = max(1, current_rank - self.filter_boost)

    def apply_whitelist(self, whitelist_set):
        """Entfernt Domains, die auf der Whitelist stehen [cite: 2026-01-11]."""
        count = 0
        for domain in whitelist_set:
            if domain in self.data:
                del self.data[domain]
                count += 1
        print(f"✅ {count} Whitelist-Treffer aus der Master-Tabelle entfernt.")

    def generate_status_json(self, output_dir):
        stats = {
            "total_domains": len(self.data),
            "categories": {},
            "last_update": datetime.now().isoformat()
        }
        for info in self.data.values():
            for cat in info["categories"]:
                stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
        with open(os.path.join(output_dir, "status.json"), "w") as f:
            json.dump(stats, f, indent=4)

    def get_export_data(self, limit=150000):
        export_list = []
        for domain, info in self.data.items():
            cat_list = list(info["categories"])
            primary_cat = cat_list[0] if cat_list else "unknown"
            export_list.append({"d": domain, "c": primary_cat, "r": info["rank"]})
        export_list.sort(key=lambda x: x["r"])
        return [{"d": item["d"], "c": item["c"]} for item in export_list[:limit]]