import os
import json
import csv

class DataExporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir

    def export_json(self, domain_list, filename="xinet_data.json"):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(domain_list, f, indent=2)
        return path

    def export_csv(self, domain_list, filename="xinet_data.csv"):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["domain"])
            for d in domain_list:
                writer.writerow([d])
        return path