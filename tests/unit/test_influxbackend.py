"""Module to test the Influx Backend.

Unit tests to check fail and success cases in Influx Backend module. The tests
can be organized in two parts. The first consists the tests to private methods
for the module are the tests for the InfluxBackend class.
isort:skip_file
"""
import sys

# pylint: disable=wrong-import-order,wrong-import-position

from unittest import TestCase, mock

sys.modules['influxdb'] = mock.MagicMock()
sys.modules['influxdb.exceptions'] = mock.MagicMock()

import napps.kytos.kronos.backends.influx as influx
from napps.kytos.kronos.utils import (BackendError, NamespaceError,
                                      ValueConvertError)

# pylint: enable=wrong-import-order,wrong-import-position
# pylint: disable=R0904,E0012, Too many public methods


class TestInfluxBackend(TestCase):
    """Test methods in Influx Backend."""

    def setUp(self):
        """Start Influx Backend."""
        settings = mock.MagicMock()
        self.backend = influx.InfluxBackend(settings)

        # The original_write_points allow to recover the original write_points
        # method. The is necessary beacause in test_write_endpoints_fail
        # the method is mocked to raise a specific influxdb exception.
        self.original_write_points = self.backend._client.write_points

        # This step is allow recover the original _query_assemble a similar
        # case as metioned above.
        self.original_query_assemble = influx._query_assemble

    def tearDown(self):
        """Reset write_points to original."""
        self.backend._client.write_points = self.original_write_points
        influx._query_assemble = self.original_query_assemble

    # First part: Testing private methods of Influx Backend module.
    def test_query_assemble_select(self):
        """Test query_assemble with SELECT clause."""
        clause = 'SELECT'
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        start = '1970-01-02T10:17:36Z'
        end = '1971-02-03T10:17:36Z'
        field = 'bytes_in'
        method = None
        group = None
        fill = None

        query = influx._query_assemble(clause, namespace, start, end,
                                              field, method, group, fill)
        expected_query = (f'SELECT bytes_in FROM "{namespace}" WHERE time  >= '
                          f'\'{str(start)}\' AND time <=\'{str(end)}\'')
        self.assertEqual(query, expected_query)

    def test_query_assemble_select_with_start_equals_none(self):
        """Test query_assemble with SELECT clause."""
        clause = 'SELECT'
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        start = None
        end = '1971-02-03T10:17:36Z'
        field = 'bytes_in'
        method = None
        group = None
        fill = None

        query = influx._query_assemble(clause, namespace, start, end,
                                              field, method, group, fill)
        expected_query = (f'SELECT bytes_in FROM "{namespace}" WHERE '
                          f'time <= \'{str(end)}\'')
        self.assertEqual(query, expected_query)

    def test_query_assemble_select_with_method_equals_median(self):
        """Test query_assemble with SELECT clause."""
        clause = 'SELECT'
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        start = '1970-01-02T10:17:36Z'
        end = '1971-02-03T10:17:36Z'
        field = 'bytes_in'
        method = 'median'
        group = None
        fill = None

        query = influx._query_assemble(clause, namespace, start, end,
                                              field, method, group, fill)
        expected_query = (f'SELECT median(bytes_in) FROM "{namespace}"'
                          f' WHERE time  >= \'{str(start)}\' AND time <'
                          f'=\'{str(end)}\'')
        self.assertEqual(query, expected_query)

    def test_query_assemble_select_with_field_equals_none(self):
        """Test query_assemble with SELECT clause with field = None."""
        clause = 'SELECT'
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        start = '1970-01-02T10:17:36Z'
        end = '1971-02-03T10:17:36Z'
        field = None
        method = None
        group = None
        fill = None

        query = influx._query_assemble(clause, namespace, start, end,
                                              field, method, group, fill)
        expected_query = (f'SELECT * FROM "{namespace}" WHERE time  >= '
                          f'\'{str(start)}\' AND time <=\'{str(end)}\'')
        self.assertEqual(query, expected_query)

    def test_query_assemble_delete(self):
        """Test query_assemble with DELETE clause."""
        clause = 'DELETE'
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        start = '1970-01-02T10:17:36Z'
        end = '1971-02-03T10:17:36Z'
        field = 'bytes_in'
        method = None
        group = None
        fill = None

        query = influx._query_assemble(clause, namespace, start, end,
                                              field, method, group, fill)
        expected_query = (f'DELETE FROM "{namespace}" WHERE time  >= '
                          f'\'{str(start)}\' AND time <=\'{str(end)}\'')
        self.assertEqual(query, expected_query)

    def test_query_assemble_error(self):
        """Test query_assemble with DELETE clause."""
        clause = ''
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        start = '1970-01-02T10:17:36Z'
        end = '1971-02-03T10:17:36Z'
        field = 'bytes_in'
        method = None
        group = None
        fill = None

        with self.assertRaises(BackendError):
            influx._query_assemble(clause, namespace, start, end, field,
                                          method, group, fill)

    def test_query_assemble_group_and_fill_options(self):
        """Test SELECT query using group and fill options."""
        clause = 'SELECT'
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        start = '1970-01-02T10:17:36Z'
        end = '1971-02-03T10:17:36Z'
        field = 'bytes_in'
        method = None
        group = '*'

        # Reports no timestamp and no value for time intervals with no data.
        fill = 'none'

        query = influx._query_assemble(clause, namespace, start, end,
                                              field, method, group, fill)
        expected_query = (f'SELECT bytes_in FROM "{namespace}" WHERE time  >= '
                          f'\'{str(start)}\' AND time <=\'{str(end)}\' '
                          f'GROUP BY time(*) fill(none)')
        self.assertEqual(query, expected_query)

    def test_validate_namespace_success(self):
        """Test to check the success in namespace validation."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'

        result = influx._validate_namespace(namespace)

        self.assertEqual(result, True)

    def test_validate_namespace_fail_with_invalid_namespace_value(self):
        """Test validate_namespace when its called with invalid value."""
        namespace = 1234

        with self.assertRaises(TypeError):
            influx._validate_namespace(namespace)

    def test_validate_namespace_fail_without_prefix(self):
        """Test validate_namespace when its called without prefix."""
        namespace = 'telemetry.switches.1.interfaces.232.bytes_in'

        with self.assertRaises(NamespaceError):
            influx._validate_namespace(namespace)

    def test_extract_field(self):
        """Test extract_field method."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'

        result = influx._extract_field(namespace)

        expected_value = ('kytos.kronos.telemetry.switches.1.interfaces.232',
                          'bytes_in')

        self.assertEqual(result, expected_value)

    # Second part: Testing methods of InfluxBackend class.
    @mock.patch('napps.kytos.kronos.backends.influx.InfluxBackend.'
                '_write_endpoints')
    def test_save_success(self, mock_influx_write_endpoints):
        """Test to check the success in data storage in Influx Backend."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        value = '1234'
        timestamp = '0'
        self.backend.save(namespace, value, timestamp)

        # Expected data to be used in _write_endpoints call.
        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'

        data = [{
                'measurement': measurement,
                'time': '1970-01-01T00:00:00Z',
                'fields': {'bytes_in': 1234.0}
                }]

        mock_influx_write_endpoints.assert_called_with(data)

    def test_save_fail_invalid_value(self):
        """Test fail case in save with invalid value."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        value = 'abc'
        timestamp = '1970-01-02T10:17:36Z'

        with self.assertRaises(ValueConvertError):
            self.backend.save(namespace, value, timestamp)

    @mock.patch('napps.kytos.kronos.backends.influx.InfluxBackend.'
                '_namespace_exists', return_value=True)
    @mock.patch('napps.kytos.kronos.backends.influx.InfluxBackend._get_points')
    def test_get_success(self, mock_influx_get_points,
                         mock_influx_namespace_exists):
        """Test to check the success in data retrieve in Influx Backend."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        start = '0'
        end = '1000000'

        self.backend.get(namespace, start, end)

        # Expected data to be used in _get_points call.
        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        field = 'bytes_in'
        method = None
        fill = None
        group = None
        start = '1970-01-01T00:00:00Z'
        end = '1970-01-12T13:46:40Z'
        mock_influx_get_points.assert_called_with(measurement, start, end,
                                                  field, method, fill, group)

    def test_get_fail_invalid_namespace(self):
        """Test fail case in save with namespace that not exists."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        start = '1971-02-03T10:17:36Z'
        end = '1970-01-02T10:17:36Z'

        self.backend._namespace_exists = mock.MagicMock()
        self.backend._namespace_exists.return_value = False
        with self.assertRaises(NamespaceError):
            self.backend.get(namespace, start, end)

    def test_get_fail_invalid_range(self):
        """Test fail case in get with invalid timestamp range."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        start = None
        end = None

        influx.validate_timestamp.return_value = False
        self.backend._namespace_exists = mock.MagicMock()
        self.backend._namespace_exists.return_value = True
        with self.assertRaises(ValueError):
            self.backend.get(namespace, start, end)

    def test_get_fail_end_smaller_than_start(self):
        """Test fail case in get with end smaller that start timestamp."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        start = '1971-02-03T10:17:36Z'
        end = '1970-01-02T10:17:36Z'

        self.backend._namespace_exists = mock.MagicMock()
        self.backend._namespace_exists.return_value = True

        with self.assertRaises(ValueError):
            self.backend.get(namespace, start, end)

    @mock.patch('napps.kytos.kronos.backends.influx.InfluxBackend.'
                '_namespace_exists', return_value=True)
    @mock.patch('napps.kytos.kronos.backends.influx.InfluxBackend.'
                '_delete_points')
    def test_delete_success(self, mock_influx_delete_points,
                            mock_influx_namespace_exists):
        """Test to check the success in data retrieve in Influx Backend."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        start = '0'
        end = '1000000'

        self.backend.delete(namespace, start, end)

        # Expected data to be used in _write_endpoints call.
        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        start = '1970-01-01T00:00:00Z'
        end = '1970-01-12T13:46:40Z'
        mock_influx_delete_points.assert_called_with(measurement, start, end)

    def test_delete_fail_invalid_namespace(self):
        """Test fail case in save with namespace that not exists."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        start = '1971-02-03T10:17:36Z'
        end = '1970-01-02T10:17:36Z'

        self.backend._namespace_exists = mock.MagicMock()
        self.backend._namespace_exists.return_value = False
        with self.assertRaises(NamespaceError):
            self.backend.delete(namespace, start, end)

    def test_delete_fail_end_smaller_than_start(self):
        """Test fail case in delete with end smaller than start."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        start = '1971-02-03T10:17:36Z'
        end = '1970-01-02T10:17:36Z'

        self.backend._namespace_exists = mock.MagicMock()
        self.backend._namespace_exists.return_value = True

        with self.assertRaises(ValueError):
            self.backend.delete(namespace, start, end)

    def test_read_config_fail_not_dbname(self):
        """Test method _read_config with missing dbname."""
        settings = mock.MagicMock()
        settings.BACKENDS = {'INFLUXDB': {'USER': 'foo',
                                          'PASS': 'bar',
                                          'PORT': 8086,
                                          'HOST': 'localhost',
                                          'DBNAME': None}
                             }

        influxbackend = influx.InfluxBackend(settings)

        influxbackend._read_config(settings)
        self.assertEqual(influxbackend._username, 'foo')
        self.assertEqual(influxbackend._password, 'bar')
        self.assertEqual(influxbackend._port, 8086)
        self.assertEqual(influxbackend._host, 'localhost')
        self.assertEqual(influxbackend._database, None)

    def test_create_database(self):
        """Test method _create_databse."""
        self.backend._create_database()
        database = self.backend._database
        self.backend._client.create_database.assert_called_with(database)

    def test_write_endpoints_success(self):
        """Test method write_endpoints."""
        self.backend._get_database = mock.MagicMock()
        self.backend._get_database.return_value = False

        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'

        data = [{
                'measurement': measurement,
                'time': '1970-01-02T10:17:36Z',
                'fields': {'bytes_in': 1234.0}
                }]

        self.backend._client.write_points.assert_called_with(data)

    def test_write_endpoints_fail(self):
        """Test fail case in method write_endpoints."""
        self.backend._client._get_database = mock.MagicMock()
        self.backend._client._get_database.return_value = False

        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'

        data = [{
                'measurement': measurement,
                'time': '1970-01-02T10:17:36Z',
                'fields': {'bytes_in': 1234.0}
                }]

        # Inside the method _write_endpoints a fail case should raise an
        # exceptions.InfluxDBClientError. Once the module exceptions is mocked
        # we have no access to that specific exception. This test works repla-
        # cing the InfluxDBClientError by Exception.
        influx.exceptions.InfluxDBClientError = Exception

        self.backend._client.write_points.side_effect = Exception

        with self.assertRaises(BackendError):
            self.backend._write_endpoints(data)

    def test_get_database_success(self):
        """Test to check the success the get_database method."""
        self.backend._database = 'database_1'

        list_db = [{'name': 'database_1'}]
        self.backend._client.get_list_database.return_value = list_db

        result = self.backend._get_database()

        self.assertEqual(result, True)

    def test_get_database_fail(self):
        """Test to check the success the get_database method."""
        self.backend._database = None

        list_db = [{'name': 'database_1'}]
        self.backend._client.get_list_database.return_value = list_db

        result = self.backend._get_database()

        self.assertEqual(result, False)

    def test_delete_points(self):
        """Test method _get_points."""
        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        start = '1970-01-02T10:17:36Z'
        end = '1971-02-03T10:17:36Z'

        query = ('SELECT bytes_in FROM "kytos.kronos.telemetry.switches.1.inte'
                 'rfaces.232" WHERE time >=\'1970-01-02T10:17:36Z\' AND time <'
                 '=\'1971-02')

        # This step is allow recover the original _query_assemble

        influx._query_assemble = mock.MagicMock()
        influx._query_assemble.return_value = query

        self.backend._delete_points(measurement, start, end)
        self.backend._client.query.assert_called_with(query)

    def test_get_points(self):
        """Test method _get_points."""
        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        field = 'bytes_in'
        method = None
        fill = None
        group = None
        start = '1970-01-02T10:17:36Z'
        end = '1971-02-03T10:17:36Z'

        query = ('SELECT bytes_in FROM "kytos.kronos.telemetry.switches.1.inte'
                 'rfaces.232" WHERE time >=\'1970-01-02T10:17:36Z\' AND time <'
                 '=\'1971-02')

        influx._query_assemble = mock.MagicMock()
        influx._query_assemble.return_value = query

        self.backend._get_points(measurement, start, end, field, method,
                                       fill, group)

        self.backend._client.query.assert_called_with(query,
                                                            chunked=True,
                                                            chunk_size=0)

    def test_get_points_fail(self):
        """Test method _get_points fail case."""
        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        field = 'bytes_in'
        method = None
        fill = None
        group = None
        start = '1970-01-02T10:17:36Z'
        end = '1971-02-03T10:17:36Z'

        query = ('SELECT bytes_in FROM "kytos.kronos.telemetry.switches.1.inte'
                 'rfaces.232" WHERE time >=\'1970-01-02T10:17:36Z\' AND time <'
                 '=\'1971-02')

        influx._query_assemble = mock.MagicMock()
        influx._query_assemble.return_value = query

        self.backend._client.query.side_effect = KeyError

        with self.assertRaises(influx.InvalidQueryError):
            self.backend._get_points(measurement, start, end, field,
                                           method, fill, group)

    def test_namespace_exists_success(self):
        """Test method _namespace_exists."""
        self.backend._client.get_list_measurements = mock.MagicMock()
        mock_measurements = self.backend._client.get_list_measurements
        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        mock_measurements.return_value = [{'name': measurement}]

        returned_value = self.backend._namespace_exists(measurement)
        self.assertEqual(returned_value, True)

    def test_namespace_exists_fail_with_none_value(self):
        """Test method _namespace_exists with namespace equals None."""
        self.backend._client.get_list_measurements = mock.MagicMock()
        mock_measurements = self.backend._client.get_list_measurements
        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        mock_measurements.return_value = [{'name': measurement}]

        returned_value = self.backend._namespace_exists(None)
        self.assertEqual(returned_value, False)

    def test_namespace_exists_fail_empty_measurement_list(self):
        """Test method _namespace_exists when there is no measuremt in db."""
        self.backend._client.get_list_measurements = mock.MagicMock()
        mock_measurements = self.backend._client.get_list_measurements
        measurement = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        mock_measurements.return_value = None

        returned_value = self.backend._namespace_exists(measurement)
        self.assertEqual(returned_value, False)

    def test_namespace_exists_fail_measurement_is_not_in_list(self):
        """Test method _namespace_exists when measurement is not in list."""
        self.backend._client.get_list_measurements = mock.MagicMock()
        mock_measurements = self.backend._client.get_list_measurements
        measurement_a = 'kytos.kronos.telemetry.switches.1.interfaces.232'
        mock_measurements.return_value = [{'name': measurement_a}]

        measurement_b = 'kytos.kronos.telemetry.switches.1.interfaces.300'

        returned_value = self.backend._namespace_exists(measurement_b)
        self.assertEqual(returned_value, False)
