"""Utility features for all backends."""
import re
from datetime import datetime

from kytos.core import log


def now():
    """Return timestamp in ISO-8601 format."""
    return datetime.utcnow().isoformat()


def validate_timestamp(start, end):
    """Validate the time stamp avoiding that the end be smaller than start."""
    if start is not None and end is not None:
        start, end = str(start), str(end)
        if start > end:
            log.error("Invalid Data Range: {}, {}".format(start, end))
            return 400
    return None


def iso_format_validation(timestamp):
    """Verify if a timestamp is in isoformat.If it's not, try to convert it."""
    if timestamp is None:
        return timestamp

    if not isinstance(timestamp, str):
        timestamp = str(timestamp)

    first_part = "(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-"
    second_part = "(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):"
    third_part = "([0-5][0-9])(\\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5]"\
                 "[0-9])"

    regex = first_part + second_part + third_part
    regex_iso = r'^(-?'+regex+'?$'
    regex_date = r'^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))'

    match_iso = re.compile(regex_iso).match
    match_date = re.compile(regex_date).match

    if match_iso(timestamp) is None and match_date(timestamp) is None:
        try:
            timestamp = float(timestamp)
            iso = '%Y-%m-%dT%H:%M:%SZ'
            timestamp = datetime.utcfromtimestamp(timestamp).strftime(iso)
        except ValueError:
            log.error("Error. Timestamp is not is ISO-8601 format.")
            return 400

    return timestamp
