import re

def normalize_domain(raw_line):
    # 1. Leerzeichen entfernen und kleinschreiben
    line = raw_line.strip().lower()
    
    # 2. Kommentare oder leere Zeilen sofort ignorieren
    if not line or line.startswith(('#', '!', ';', '//')):
        return None
        
    # 3. Hosts-Format behandeln (z.B. "0.0.0.0 domain.com" oder "127.0.0.1 domain.com")
    # Wir nehmen einfach das letzte Element der Zeile
    parts = line.split()
    domain = parts[-1]
    
    # 4. Protokolle und WWW entfernen
    domain = re.sub(r"^(https?://)?(www\.)?", "", domain)
    
    # 5. Pfade oder Parameter abschneiden
    domain = domain.split('/')[0].split('?')[0]
    
    # 6. Deine "ss"-Regel
    domain = domain.replace("ß", "ss")
    
    # 7. Validierung: Muss wie eine echte Domain aussehen
    if re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", domain):
        return domain
    return None
