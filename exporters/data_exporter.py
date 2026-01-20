import os
import json
import csv

class DataExporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir

    def export_web_json(self, master_data, filename="xinet_data.json", limit=100000):
        """
        Erstellt eine JSON-Datei, die Domains UND Kategorien enthaelt.
        Format: [{"d": "domain.com", "c": "sex"}, ...]
        """
        path = os.path.join(self.output_dir, filename)
        
        # Wir sortieren nach Ranking und nehmen die Top-Eintraege
        sorted_domains = sorted(
            master_data.items(),
            key=lambda x: x[1]['rank'] if x[1]['rank'] is not None else 9999999
        )[:limit]
        
        web_data = []
        for domain, info in sorted_domains:
            web_data.append({
                "d": domain,
                "c": info['category']
            })
            
        with open(path, "w", encoding="utf-8") as f:
            json.dump(web_data, f, separators=(',', ':')) # Kompakt speichern
        return path

    def export_csv(self, domain_list, filename="xinet_data.csv"):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["domain"])
            for d in domain_list:
                writer.writerow([d])
        return path