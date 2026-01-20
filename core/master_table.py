class MasterTable:
    def __init__(self):
        # Struktur: { "domain.com": {"categories": set(), "rank": 9999999} }
        self.data = {}
        self.default_rank = 1000000  # Alles, was nicht in den Top-Listen ist

    def add_domain(self, domain, category, rank=None):
        """Fügt eine Domain hinzu oder aktualisiert Kategorien/Rank."""
        if domain not in self.data:
            self.data[domain] = {
                "categories": {category},
                "rank": rank if rank is not None else self.default_rank
            }
        else:
            # Kategorie hinzufügen (Deduplizierung passiert durch das Set automatisch)
            self.data[domain]["categories"].add(category)
            # Wenn ein besserer (niedrigerer) Rank gefunden wird, aktualisieren
            if rank is not None and rank < self.data[domain]["rank"]:
                self.data[domain]["rank"] = rank

    def apply_whitelist(self, whitelist_set):
        """Entfernt alle Domains, die auf der Whitelist stehen."""
        for domain in whitelist_set:
            if domain in self.data:
                del self.data[domain]

    def get_filtered_list(self, target_categories, limit=None):
        """
        Extrahiert die Liste basierend auf User-Wunsch.
        Sortiert nach Rank (niedrigster zuerst = wichtigste Seiten).
        """
        result = []
        for domain, info in self.data.items():
            # Prüfen, ob die Domain in einer der gewünschten Kategorien ist
            if any(cat in target_categories for cat in info["categories"]):
                result.append((domain, info["rank"]))

        # Sortieren nach Rank
        result.sort(key=lambda x: x[1])

        # Limiter anwenden (unser Export-Limiter aus der GUI)
        if limit:
            result = result[:limit]
        
        return [item[0] for item in result]
