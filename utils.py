"""Utility features for all backends."""
import re
from datetime import datetime


class InvalidNamespaceError(Exception):
    """Exception thrown when the provided namespace is not valid."""


class ValueConvertError(Exception):
    """Exception thrown when it is not possible convert the value to stored."""


class NamespaceNotExistsError(Exception):
    """Exception thrown when the provided namespace does not exist."""


class TimestampRangeError(Exception):
    """Exception thrown when the provided range timestamp is not valid."""


def now():
    """Return timestamp in ISO-8601 format."""
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def validate_timestamp(start, end):
    """Validate timestamp to avoid that end be smaller than start."""
    if start is not None and end is not None:
        start, end = str(start), str(end)
        if start > end:
            return False
    return True


def convert_to_iso(timestamp):
    """Convert a value to ISO-8601 format."""
    try:
        timestamp = float(timestamp)
        iso = '%Y-%m-%dT%H:%M:%SZ'
        timestamp = datetime.utcfromtimestamp(timestamp).strftime(iso)
        return timestamp
    except ValueError:
        error = f'Error: Timestamp value \'{timestamp}\' is not convertible'\
                 ' to ISO-8601 format.'
        raise ValueConvertError(error)
    except OverflowError:
        error = f'Error: Timestamp \'{timestamp}\' float value is too '\
                 'large to be used as datetime.'
        raise ValueConvertError(error)


def iso_format_validation(timestamp):
    """Verify if a timestamp is in isoformat."""
    if timestamp is None:
        return False

    first_part = "(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-"
    second_part = "(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):"
    third_part = "([0-5][0-9])(\\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5]"\
                 "[0-9])"

    regex = first_part + second_part + third_part
    regex_iso = r'^(-?' + regex + '?$'
    regex_date = r'^([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))'

    match_iso = re.compile(regex_iso).match
    match_date = re.compile(regex_date).match

    if not (match_iso(timestamp) or match_date(timestamp)):
        return False

    return True
