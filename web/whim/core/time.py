from datetime import datetime, timezone, time


def zero_time_with_timezone(date, tz=timezone.utc):
    return datetime.combine(date, time(tzinfo=tz))