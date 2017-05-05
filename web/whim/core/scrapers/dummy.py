from .base import BaseScraper


class DummyScraper(BaseScraper):
    def run(self):
        return [{}]
