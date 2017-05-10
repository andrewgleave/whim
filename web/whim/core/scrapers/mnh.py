from datetime import datetime, timezone, time
import re

import requests
from bs4 import BeautifulSoup

from django.db import transaction

from .base import BaseScraper
from .exceptions import ScraperException

from whim.core.models import Event, Source, Category
from whim.core.utils import get_object_or_none
from whim.core.time import zero_time_with_timezone, attempt_parse_date

DATE_CLEAN_REGEX = re.compile('[^\w\s\/]', re.IGNORECASE)


class MNHScraper(BaseScraper):
    def split_dates(self, date):
        clean = DATE_CLEAN_REGEX.sub('', date)
        split = clean.split(' ')
        return [x for x in split if x != '']

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
                    "category": e.find("span", {"class": "badge"}).string,
                    "status": Event.STATUS_PENDING,
                    "start_date": None,
                    "end_date": None
                }
                # get rest of data
                article = e.find("div", {"class": "text"})
                if article:
                    tmp["name"] = article.contents[0].string  # h2
                    tmp["description"] = article.contents[3].contents[
                        0].string  # p
                    # dates
                    try:
                        dates = article.contents[2].contents[0].string  # span
                        split = self.split_dates(dates)
                        if len(split) > 0:
                            start_date = attempt_parse_date(split[0])
                            if start_date is not None:
                                tmp["start_date"] = zero_time_with_timezone(
                                    start_date)
                        if len(split) > 1:
                            # assume last in list is probably a date
                            end_date = attempt_parse_date(split[-1])
                            if end_date is not None:
                                tmp["end_date"] = zero_time_with_timezone(
                                    end_date)
                    except:
                        pass
                    # if we have missing dates, mark for review
                    if not tmp["start_date"] or not tmp["end_date"]:
                        tmp["status"] = Event.STATUS_NEEDS_REVIEW
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
                    status=scraped_event["status"],
                    name=scraped_event["name"],
                    description=scraped_event["description"],
                    start_datetime=scraped_event["start_date"],
                    end_datetime=scraped_event["end_date"],
                    link=scraped_event["link"],
                    tags=[])
            else:
                # update existing here in case details have changed?
                pass
        # mark
        source.last_run_date = datetime.now(timezone.utc)
        source.save()
