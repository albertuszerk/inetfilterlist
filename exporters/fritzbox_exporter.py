import os

class FritzboxExporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export(self, domain_list, filename="xinet_fritzbox.txt"):
        """Erstellt eine einfache Textliste fuer die Fritz!Box."""
        file_path = os.path.join(self.output_dir, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for domain in domain_list:
                    f.write(f"{domain}\n")
            return file_path
        except Exception as e:
            print(f"Fehler beim Fritz!Box-Export: {e}")
            return None