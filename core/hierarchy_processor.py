
class HierarchyProcessor:
    def __init__(self):
        pass

    def clean_redundancies(self, domain_list):
        """
        Entfernt Subdomains, wenn die Hauptdomain bereits vorhanden ist.
        Beispiel: ['seite.de', 'www.seite.de'] -> ['seite.de']
        """
        # 1. Schritt: Sortieren nach der Anzahl der Labels (Punkte)
        # Kurze Domains (z.B. seite.de) kommen vor langen (www.seite.de)
        sorted_domains = sorted(domain_list, key=lambda x: x.count('.'))
        
        final_list = []
        blocked_roots = set()

        # 2. Schritt: Analyse der Eltern-Kind-Beziehung
        for domain in sorted_domains:
            is_redundant = False
            parts = domain.split('.')
            
            # Wir prüfen von hinten nach vorne, ob ein Teil der Domain schon gesperrt ist
            # Beispiel 'm.intern.seite.de':
            # Check 1: 'de' (wird ignoriert)
            # Check 2: 'seite.de' -> Ist das schon in blocked_roots?
            # Check 3: 'intern.seite.de' -> Ist das schon in blocked_roots?
            for i in range(len(parts) - 1, 0, -1):
                parent_candidate = ".".join(parts[i:])
                if parent_candidate in blocked_roots:
                    is_redundant = True
                    break
            
            if not is_redundant:
                final_list.append(domain)
                blocked_roots.add(domain)
        
        return final_list
