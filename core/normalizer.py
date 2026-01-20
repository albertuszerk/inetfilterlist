import re

def normalize_domain(raw_line):
    # 1. Alles kleinschreiben
    domain = raw_line.lower().strip()
    
    # 2. Protokolle und WWW entfernen
    domain = re.sub(r"^(https?://)?(www\.)?", "", domain)
    
    # 3. Pfade oder Parameter nach der Domain abschneiden (z.B. seite.de/pfad -> seite.de)
    domain = domain.split('/')[0].split('?')[0]
    
    # 4. Deine "ss"-Regel anwenden
    domain = domain.replace("ß", "ss")
    
    # 5. Validierung: Muss wie eine Domain aussehen
    # (Buchstaben, Zahlen, Bindestrich und mindestens ein Punkt)
    if re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", domain):
        return domain
    return None
