class BaseScraper:
    """Abstract scraper"""

    def run(self):
        raise NotImplementedError("Subclass this and override run")