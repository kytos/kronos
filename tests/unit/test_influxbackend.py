"""Module to test the Influx Backend."""
# from unittest import TestCase
#
# from napps.kytos.kronos import settings
# from napps.kytos.kronos.backends.influx import InfluxBackend
# from napps.kytos.kronos.utils import (InvalidNamespaceError,
#                                      NamespaceNotExistsError,
#                                      ValueConvertError, now)
#
#
# class TestInfluxBackend(TestCase):
#    """Test methods in Influx Backend."""
#
#    influxbackend = None
#
#    def setUp(self):
#        """Create object of influxdb to be used in tests."""
#        self.influxbackend = InfluxBackend(settings)
#
#    def tearDown(self):
#        """Close conections of influxdb."""
#        self.influxbackend._client.close()
#
#    def test_save_success(self):
#        """Test to check the success in data storage in Influx Backend."""
#       namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
#        value = '1324'
#        timestamp = now()
#
#        result = self.influxbackend.save(namespace, value, timestamp)
#
#        self.assertEqual(None, result)
#
#    def test_save_failed_namespace_without_prefix(self):
#        """Test case where prefix 'kytos.kronos' is not in namespace."""
#        namespace = 'telemetry.switches.1.interfaces.232.bytes_in'
#        value = '1324'
#        timestamp = now()
#
#        with self.assertRaises(InvalidNamespaceError):
#            self.influxbackend.save(namespace, value, timestamp)
#
#    def test_save_failed_namespace_not_string(self):
#        """Test case where namespace is not a string type."""
#        namespace = 1234
#        value = '1324'
#        timestamp = now()
#
#        with self.assertRaises(TypeError):
#            self.influxbackend.save(namespace, value, timestamp)
#
#    def test_save_failed_invalid_value(self):
#        """Test case where the value to store is not float."""
#       namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
#        value = 'invalid value'
#        timestamp = now()
#
#        with self.assertRaises(ValueConvertError):
#            self.influxbackend.save(namespace, value, timestamp)
#
#    def test_get_success(self):
#        """Test to check success in data retrieving in Influx Backend."""
#       namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
#        value = 1324
#        timestamp = now()
#
#        self.influxbackend.save(namespace, str(value), timestamp)
#
#        results = self.influxbackend.get(namespace, start=timestamp)
#        expected_store_value = [[timestamp, value]]
#
#        self.assertEqual(expected_store_value, results)
#
#    def test_delete_success(self):
#        """Test to check success deleting data in Influx Backend."""
#       namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
#        value = 1324
#        timestamp = now()
#
#        with self.assertRaises(NamespaceNotExistsError):
#            self.influxbackend.save(namespace, value, timestamp)
#            self.influxbackend.delete(namespace, str(value), timestamp)
#            self.influxbackend.get(namespace, start=timestamp)
