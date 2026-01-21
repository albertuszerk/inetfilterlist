import os
import json

class DataExporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir

    def export_web_json(self, master_data, filename="xinet_data.json", limit=150000):
        path = os.path.join(self.output_dir, filename)
        
        # Sortierung nach Ranking
        sorted_domains = sorted(
            master_data.items(),
            key=lambda x: x[1].get('rank') if isinstance(x[1], dict) and x[1].get('rank') is not None else 9999999
        )[:limit]
        
        web_data = []
        for domain, info in sorted_domains:
            # Sicherheits-Check: Ist info ein Dictionary und hat es den Key 'category'?
            if isinstance(info, dict):
                # Wir suchen nach 'category' oder 'cat' (beugt Fehlern vor)
                category = info.get('category') or info.get('cat') or "unknown"
            else:
                # Falls info nur ein String ist (alter Fehlerzustand)
                category = "unknown"
                
            web_data.append({
                "d": domain,
                "c": category
            })
            
        with open(path, "w", encoding="utf-8") as f:
            json.dump(web_data, f, separators=(',', ':')) 
        
        print(f"Erfolgreich exportiert: {path} ({len(web_data)} Eintraege)")
        return path