from datetime import datetime, timezone, time

import dateparser


def zero_time_with_timezone(date, tz=timezone.utc):
    return datetime.combine(date, time(tzinfo=tz))


def attempt_parse_date(val):
    parsed_date = dateparser.parse(val, languages=['en'])
    if parsed_date is None:
        # try other strategies?
        pass
    return parsed_date