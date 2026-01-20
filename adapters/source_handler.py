import requests
import tarfile
import io
from core.normalizer import normalize_domain

class SourceHandler:
    def __init__(self):
        self.timeout = 15  # Sekunden, bevor der Download abgebrochen wird

    def fetch_plain_text(self, url):
        """Lädt eine einfache Textliste herunter und normalisiert sie."""
        domains = set()
        try:
            response = requests.get(url, timeout=self.timeout, stream=True)
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        # Kommentare ignorieren
                        if not line.startswith(('#', '//', ';')):
                            normalized = normalize_domain(line)
                            if normalized:
                                domains.add(normalized)
            return domains
        except Exception as e:
            print(f"Fehler beim Laden von {url}: {e}")
            return set()

    def fetch_tar_gz(self, url, target_file_name="domains"):
        """
        Lädt ein .tar.gz Archiv (z.B. UT1) und extrahiert 
        Inhalte direkt im Arbeitsspeicher.
        """
        domains = set()
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                # Das Archiv im Arbeitsspeicher öffnen (kein lokales Speichern!)
                with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tar:
                    for member in tar.getmembers():
                        # Wir suchen nach Dateien, die die Domain-Listen enthalten
                        if member.isfile() and target_file_name in member.name:
                            f = tar.extractfile(member)
                            if f:
                                content = f.read().decode('utf-8', errors='ignore')
                                for line in content.splitlines():
                                    normalized = normalize_domain(line)
                                    if normalized:
                                        domains.add(normalized)
            return domains
        except Exception as e:
            print(f"Fehler beim Verarbeiten des Archivs von {url}: {e}")
            return set()

# Beispielhafter Aufruf (für Testzwecke):
# handler = SourceHandler()
# list_sex = handler.fetch_tar_gz("https://.../porn.tar.gz")
