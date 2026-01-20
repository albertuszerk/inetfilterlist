import re

def normalize_domain(raw_line):
    line = raw_line.strip().lower()
    if not line or line.startswith(('#', '!', ';', '//')):
        return None
        
    # Extrahiert die Domain, auch wenn eine IP davor steht
    parts = line.split()
    domain = parts[-1]
    
    domain = re.sub(r"^(https?://)?(www\.)?", "", domain)
    domain = domain.split('/')[0].split('?')[0]
    domain = domain.replace("ß", "ss")
    
    if re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", domain):
        return domain
    return None
