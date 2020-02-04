"""Module to test the CSV Backend."""
# from unittest import TestCase
#
# from napps.kytos.kronos import settings
# from napps.kytos.kronos.backends.csvbackend import CSVBackend
# from napps.kytos.kronos.utils import now
#
#
# class TestCSVBackend(TestCase):
#    """Test methods in CSV Backend."""
#
#    def test_save_success(self):
#        """Test to check the success in data storage in CSV Backend."""
#        namespace = 'kytos.telemetry.switches.1.interfaces.232.bytes_in'
#        value = '1324'
#        timestamp = now()
#
#        csvbackend = CSVBackend(settings)
#        result = csvbackend.save(namespace, value, timestamp)
#
#        self.assertEqual(None, result)
#
#    def test_get_success(self):
#        """Test to check success in data retrieving in CSV Backend."""
#        namespace = 'kytos.telemetry.switches.1.interfaces.232.bytes_in'
#        value = '1324'
#        timestamp = now()
#
#        csvbackend = CSVBackend(settings)
#        csvbackend.save(namespace, value, timestamp)
#
#        fname = f'{csvbackend.user}_{namespace}.csv'
#
#        result = csvbackend.get(namespace, fname, start=timestamp)
#        expected_store_value = [[value, timestamp]]
#
#        self.assertEqual(expected_store_value, result)
#
#    def test_delete_sucess(self):
#        """Test to check success in data retrieving in CSV Backend."""
#        namespace = 'kytos.telemetry.switches.1.interfaces.232.bytes_in'
#        value = '1324'
#        timestamp = now()
#
#        csvbackend = CSVBackend(settings)
#        csvbackend.save(namespace, value, timestamp)
#
#        fname = f'{csvbackend.user}_{namespace}.csv'
#
#        result = csvbackend.delete(namespace, fname, start=timestamp)
#
#        self.assertEqual(None, result)
