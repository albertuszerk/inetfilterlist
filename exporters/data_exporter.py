import os
import json

class DataExporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir

    def export_web_json(self, master_data, filename="xinet_data.json", limit=150000):
        path = os.path.join(self.output_dir, filename)
        
        # Wir sortieren nach Ranking
        sorted_domains = sorted(
            master_data.items(),
            key=lambda x: x[1]['rank'] if x[1]['rank'] is not None else 9999999
        )[:limit]
        
        web_data = []
        for domain, info in sorted_domains:
            # WICHTIG: Hier wird das Objekt mit Domain (d) und Kategorie (c) gebaut
            web_data.append({
                "d": domain,
                "c": info['category']
            })
            
        with open(path, "w", encoding="utf-8") as f:
            # separators macht die Datei so klein wie moeglich
            json.dump(web_data, f, separators=(',', ':')) 
        return path