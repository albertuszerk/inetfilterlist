import requests
import tarfile
import io
import os
import hashlib
from datetime import datetime
from core.normalizer import normalize_domain

class SourceHandler:
    def __init__(self, cache_dir="cache", force_download=False):
        self.timeout = 25
        self.cache_dir = cache_dir
        self.force_download = force_download
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_path(self, url):
        """Erzeugt einen eindeutigen Dateinamen basierend auf der URL und dem Datum."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.cache_dir, f"{date_str}_{url_hash}.tmp")

    def _get_data(self, url):
        cache_path = self._get_cache_path(url)
        
        # Wenn Cache existiert und kein Force-Download aktiv ist -> Lade aus Datei
        if os.path.exists(cache_path) and not self.force_download:
            print(f"    (Nutze Cache: {url})")
            with open(cache_path, "rb") as f:
                return f.read()
        
        # Ansonsten: Neu herunterladen
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                with open(cache_path, "wb") as f:
                    f.write(response.content)
                return response.content
            print(f"    WARNUNG: Server antwortete mit {response.status_code}")
        except Exception as e:
            print(f"    FEHLER beim Laden von {url}: {e}")
        return None

    def fetch_plain_text(self, url):
        domains = set()
        content_raw = self._get_data(url)
        if content_raw:
            content = content_raw.decode('utf-8', errors='ignore')
            for line in content.splitlines():
                normalized = normalize_domain(line)
                if normalized: domains.add(normalized)
        return domains

    def fetch_tar_gz(self, url, target_file_name="domains"):
        domains = set()
        content_raw = self._get_data(url)
        if content_raw:
            try:
                with tarfile.open(fileobj=io.BytesIO(content_raw), mode="r:gz") as tar:
                    for member in tar.getmembers():
                        if member.isfile() and target_file_name in member.name:
                            f = tar.extractfile(member)
                            if f:
                                text = f.read().decode('utf-8', errors='ignore')
                                for line in text.splitlines():
                                    normalized = normalize_domain(line)
                                    if normalized: domains.add(normalized)
            except Exception as e:
                print(f"    Fehler beim Entpacken: {e}")
        return domains