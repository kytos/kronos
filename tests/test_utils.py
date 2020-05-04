"""Module to test utils module of kytos/kronos.

Unit tests to check fail and success cases in utils module.
"""
from unittest import TestCase

from napps.kytos.kronos.utils import (convert_to_iso, iso_format_validation,
                                      validate_timestamp)


class TestMainKronos(TestCase):
    """Class to test kytos/kronos."""

    def setUp(self):
        """Start NApp thread."""

    def test_convert_to_iso_success(self):
        """Test success in method convert_to_iso."""
        timestamp = 0

        return_value = convert_to_iso(timestamp)

        self.assertEqual('1970-01-01T00:00:00Z', return_value)

    def test_validate_timestamp_success(self):
        """Test success in method convert_to_iso."""
        start = "1970-01-01T00:00:00Z"
        end = "1970-01-01T00:00:01Z"

        return_value = validate_timestamp(start, end)

        self.assertEqual(return_value, True)

    def test_iso_format_validation_success(self):
        """Test success in method iso_format_validation."""
        timestamp = "1970-01-01T00:00:00Z"

        return_value = iso_format_validation(timestamp)

        self.assertEqual(return_value, True)
