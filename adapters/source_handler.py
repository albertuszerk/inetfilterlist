import requests
import tarfile
import zipfile
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
        url_hash = hashlib.md5(url.encode()).hexdigest()
        date_str = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.cache_dir, f"{date_str}_{url_hash}.tmp")

    def _get_data(self, url):
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path) and not self.force_download:
            return f.read() if False else open(cache_path, "rb").read() # Kurze Cache-Logik
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                with open(cache_path, "wb") as f:
                    f.write(response.content)
                return response.content
            print(f"    WARNUNG: Server antwortete mit {response.status_code} bei {url}")
        except Exception as e:
            print(f"    FEHLER beim Laden von {url}: {e}")
        return None

    def fetch(self, url):
        if url.endswith(".tar.gz"):
            return self.fetch_tar_gz(url)
        return self.fetch_plain_text(url)

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

    def download_ranking(self, target_path):
        """Versucht das Ranking von Tranco zu laden, mit Cisco Umbrella als Fallback."""
        sources = [
            {"name": "Tranco", "url": "https://tranco-list.eu/download_daily/1000000"},
            {"name": "Cisco Umbrella", "url": "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"}
        ]

        for src in sources:
            print(f"Beziehe strategisches Ranking von {src['name']}...")
            content_raw = self._get_data(src['url'])
            if content_raw:
                try:
                    with zipfile.ZipFile(io.BytesIO(content_raw)) as z:
                        for file_info in z.infolist():
                            if file_info.filename.endswith(".csv"):
                                with z.open(file_info) as s_file, open(target_path, "wb") as t_file:
                                    t_file.write(s_file.read())
                                print(f"✅ Ranking erfolgreich von {src['name']} bezogen.")
                                return True
                except Exception as e:
                    print(f"⚠️ Fehler beim Verarbeiten von {src['name']}: {e}")
        
        print("❌ Alle Ranking-Quellen sind aktuell nicht erreichbar.")
        return False