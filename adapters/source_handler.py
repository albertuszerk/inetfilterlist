import requests
import tarfile
import io
from core.normalizer import normalize_domain

class SourceHandler:
    def __init__(self):
        self.timeout = 15
        # Ein Standard-User-Agent, damit Server uns nicht blockieren
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) X-iNet-Filter-Gen'
        }

    def fetch_plain_text(self, url):
        domains = set()
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, stream=True)
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        normalized = normalize_domain(line)
                        if normalized:
                            domains.add(normalized)
            return domains
        except Exception as e:
            print(f"Fehler bei {url}: {e}")
            return set()

    def fetch_tar_gz(self, url, target_file_name="domains"):
        domains = set()
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tar:
                    for member in tar.getmembers():
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
            print(f"Fehler bei Archiv {url}: {e}")
            return set()
