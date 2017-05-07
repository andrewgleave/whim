from datetime import datetime, timezone, time

import requests
from bs4 import BeautifulSoup

from django.db import transaction

from .base import BaseScraper
from .exceptions import ScraperException

from whim.core.models import Event, Source, Category
from whim.core.utils import get_object_or_none
from whim.core.time import zero_time_with_timezone


class MNHScraper(BaseScraper):
    def get_data(self):
        url = "https://manxnationalheritage.im/whats-on/"
        parsed = []
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            events = soup.select(
                "div.columns.no-padding-grid.push-top-m > div > a")
            parsed = []
            for e in events:
                tmp = {
                    "link": e.get('href'),
                    "category": e.find("span", {"class": "badge"}).string
                }
                #get rest of data
                article = e.find("div", {"class": "text"})
                if article:
                    tmp["name"] = article.contents[0].string  #h2
                    tmp["description"] = article.contents[3].contents[
                        0].string  #p
                    #dates
                    try:
                        dates = article.contents[2].contents[0].string.replace(
                            " ", "").replace("–", "-").split("-")  #span
                        tmp["start_date"] = zero_time_with_timezone(
                            datetime.strptime(dates[0], "%d/%m/%Y"))
                        if len(dates) > 1:
                            tmp["end_date"] = zero_time_with_timezone(
                                datetime.strptime(dates[1], "%d/%m/%Y"))
                    except:
                        continue
                parsed.append(tmp)
            return parsed
        else:
            raise ScraperException("Unexpected status code")

    @transaction.atomic
    def run(self, source_id):
        source = Source.objects.get(id=source_id)
        for scraped_event in self.get_data():
            event = get_object_or_none(
                Event, source=source, name=scraped_event["name"])
            if event is None:
                category, _ = Category.objects.get_or_create_from_name(
                    scraped_event["category"])
                Event.objects.create(
                    source=source,
                    category=category,
                    name=scraped_event["name"],
                    description=scraped_event["description"],
                    start_datetime=scraped_event["start_date"],
                    end_datetime=scraped_event.get("end_date"),
                    link=scraped_event["link"],
                    tags=[])
        #mark this run
        source.last_run_date = datetime.now(timezone.utc)
        source.save()
