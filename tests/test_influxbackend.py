"""Module to test the Influx Backend."""
from unittest import TestCase

from napps.kytos.kronos import settings
from napps.kytos.kronos.backends.influx import InfluxBackend
from napps.kytos.kronos.utils import (InvalidNamespaceError, ValueConvertError,
                                      now)


class TestInfluxBackend(TestCase):
    """Test methods in Influx Backend."""

    def test_save_success(self):
        """Test to check the success in data storage in Influx Backend."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        value = '1324'
        timestamp = now()

        influxbackend = InfluxBackend(settings)
        result = influxbackend.save(namespace, value, timestamp)

        influxbackend._client.close()

        self.assertEqual(None, result)

    def test_save_failed_namespace_without_prefix(self):
        """Test case where prefix 'kytos.kronos' is not in namespace."""
        namespace = 'telemetry.switches.1.interfaces.232.bytes_in'
        value = '1324'
        timestamp = now()

        influxbackend = InfluxBackend(settings)
        with self.assertRaises(InvalidNamespaceError):
            influxbackend.save(namespace, value, timestamp)
            influxbackend._client.close()

    def test_save_failed_namespace_not_string(self):
        """Test case where namespace is not a string type."""
        namespace = 1234
        value = '1324'
        timestamp = now()

        influxbackend = InfluxBackend(settings)
        with self.assertRaises(TypeError):
            influxbackend.save(namespace, value, timestamp)
            influxbackend._client.close()
 
    def test_save_failed_invalid_value(self):
        """Test case where the value to store is not float."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        value = 'invalid value'
        timestamp = now()

        influxbackend = InfluxBackend(settings)
        with self.assertRaises(ValueConvertError):
            influxbackend.save(namespace, value, timestamp)
            influxbackend._client.close()

    def test_get_success(self):
        """Test to check success in data retrieving in Influx Backend."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        value = 1324
        timestamp = now()

        influxbackend = InfluxBackend(settings)
        influxbackend.save(namespace, str(value), timestamp)

        results = influxbackend.get(namespace, start=timestamp)
        expected_store_value = [[timestamp, value]]

        influxbackend._client.close()

        self.assertEqual(expected_store_value, results)
