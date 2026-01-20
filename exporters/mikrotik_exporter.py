import os

class MikrotikExporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        # Sicherstellen, dass der Output-Ordner existiert
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export(self, domain_list, filename="xinet_blocklist.rsc"):
        """
        Erstellt ein MikroTik RouterOS Script (.rsc).
        Syntax: /ip dns static add name="domain.com" address=0.0.0.0
        """
        file_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("/ip dns static\n")
                f.write(":log info \"X-iNet: Importiere Sperrliste...\"\n")
                
                for domain in domain_list:
                    # Wir nutzen address=0.0.0.0, was für DNS-Sperren hocheffizient ist
                    f.write(f'add name="{domain}" address=0.0.0.0 comment="X-iNet Block"\n')
                
                f.write(":log info \"X-iNet: Import abgeschlossen.\"\n")
            
            print(f"Erfolgreich exportiert: {file_path} ({len(domain_list)} Einträge)")
            return file_path
        except Exception as e:
            print(f"Fehler beim Export für MikroTik: {e}")
            return None
