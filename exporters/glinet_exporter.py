import os

class GlinetExporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export(self, domain_list, filename="xinet_flint2_adguard.txt"):
        """
        Erstellt eine Filterliste im AdGuard/Hosts-Format.
        Format: ||domain.com^
        """
        file_path = os.path.join(self.output_dir, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("! Title: X-iNet Master Filter für Flint 2\n")
                f.write("! Description: Hochleistungs-Kinderschutzfilter\n")
                for domain in domain_list:
                    # Das AdGuard-Format ||domain^ blockiert die Domain und alle Subdomains
                    f.write(f"||{domain}^\n")
            return file_path
        except Exception as e:
            print(f"Fehler beim Flint 2 Export: {e}")
            return None