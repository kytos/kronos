"""Module to test main module of kytos/kronos.

Unit tests to check fail and success cases in main module.
isort:skip_file
"""
import sys
# pylint: disable=wrong-import-order,wrong-import-position
from unittest import TestCase, mock

from flask import Flask

sys.modules['influxdb'] = mock.MagicMock()

from napps.kytos.kronos.main import Main
from napps.kytos.kronos.utils import (NamespaceError)
from tests.helpers import get_controller_mock

# pylint: enable=wrong-import-order,wrong-import-position
# pylint: disable=R0904,E0012, Too many public methods


class TestMainKronos(TestCase):
    """Class to test kytos/kronos."""

    def setUp(self):
        """Start NApp thread."""
        self.napp = Main(get_controller_mock())

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.save')
    def test_rest_save_success_with_influx(self, mock_influx_save):
        """Test success in method rest_save."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        value = '123'
        timestamp = None

        app = Flask(__name__)
        with app.app_context():
            self.napp.rest_save(namespace, value, timestamp)
            mock_influx_save.assert_called_with(namespace, value, timestamp)

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.save')
    def test_rest_save_failed_namespace_without_prefix(self, mock_influx_save):
        """Test fail case in method rest_save with an invalid namespace."""
        namespace = 'telemetry.switches.1.interfaces.232.bytes_in'
        value = '123'
        timestamp = None

        mock_influx_save.side_effect = NamespaceError()

        app = Flask(__name__)
        with app.app_context():
            response = self.napp.rest_save(namespace, value, timestamp)
            exception_name = response.json['exc_name']
            self.assertEqual(exception_name, 'NamespaceError')

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.save')
    def test_rest_save_failed_converting_value(self, mock_influx_save):
        """Test fail case in method rest_save with an invalid value."""
        namespace = 'kytos.telemetry.switches.1.interfaces.232.bytes_in'
        value = '123'
        timestamp = 'abc'

        mock_influx_save.side_effect = ValueError()

        app = Flask(__name__)
        with app.app_context():
            response = self.napp.rest_save(namespace, value, timestamp)
            exception_name = response.json['exc_name']
            self.assertEqual(exception_name, 'ValueError')

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.delete')
    def test_rest_delete_success_with_influx(self, mock_influx_delete):
        """Test success in method rest_delete."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        start = 123456
        end = 123457

        app = Flask(__name__)
        with app.app_context():
            self.napp.rest_delete(namespace, start, end)
            mock_influx_delete.assert_called_with(namespace, start, end)

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.delete')
    def test_rest_delete_failed_namespace_wrong_prefix(self, mock_influx_del):
        """Test fail case in rest_delete with an invalid namespace."""
        namespace = 'telemetry.switches.1.interfaces.232.bytes_in'
        start = 123456
        end = 123457

        mock_influx_del.side_effect = NamespaceError()

        app = Flask(__name__)
        with app.app_context():
            response = self.napp.rest_delete(namespace, start, end)
            exception_name = response.json['exc_name']
            self.assertEqual(exception_name, 'NamespaceError')

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.delete')
    def test_rest_delete_failed_invalid_timestamp(self, mock_influx_del):
        """Test fail case in method rest_delete with an invalid timestamp."""
        namespace = 'kytos.telemetry.switches.1.interfaces.232.bytes_in'
        start = 'abc'
        end = 123457

        mock_influx_del.side_effect = ValueError()

        app = Flask(__name__)
        with app.app_context():
            response = self.napp.rest_delete(namespace, start, end)
            exception_name = response.json['exc_name']
            self.assertEqual(exception_name, 'ValueError')

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.delete')
    def test_rest_delete_failed_invalid_timestamp_range(self, mock_influx_del):
        """Test fail case in rest_delete with an invalid timestamp range."""
        namespace = 'kytos.telemetry.switches.1.interfaces.232.bytes_in'
        start = 22222
        end = 11111

        mock_influx_del.side_effect = ValueError()

        app = Flask(__name__)
        with app.app_context():
            response = self.napp.rest_delete(namespace, start, end)
            exception_name = response.json['exc_name']
            self.assertEqual(exception_name, 'ValueError')

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.get')
    def test_rest_get_success_with_influx(self, mock_influx_get):
        """Test success in method rest_get."""
        namespace = ('kytos.kronos.telemetry.switches.1.interfaces.232.'
                     'bytes_in.12')
        start = 123456
        end = 123457

        mock_influx_get.return_value = [['1970-01-01T00:00:00.001234567Z', 12]]

        app = Flask(__name__)
        with app.app_context():
            self.napp.rest_get(namespace, start, end)
            mock_influx_get.assert_called_with(namespace, start, end, None,
                                               None, None)

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.get')
    def test_rest_get_fail_invalid_namespace(self, mock_influx_get):
        """Test fail case in method rest_get passing an invalid namespace."""
        namespace = 'kronos.telemetry.switches.1.interfaces.232.bytes_in.12'
        start = 123456
        end = 123457

        mock_influx_get.side_effect = NamespaceError()

        app = Flask(__name__)
        with app.app_context():
            response = self.napp.rest_get(namespace, start, end)
            exception_name = response.json['exc_name']
            self.assertEqual(exception_name, 'NamespaceError')

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.get')
    def test_rest_get_fail_with_invalid_timestamp(self, mock_influx_get):
        """Test fail case in method rest_get with an invalid timestamp."""
        namespace = ('kytos.kronos.telemetry.switches.1.interfaces.232.'
                     'bytes_in.12')
        start = 'abc'
        end = 11111

        mock_influx_get.side_effect = ValueError()

        app = Flask(__name__)
        with app.app_context():
            response = self.napp.rest_get(namespace, start, end)
            exception_name = response.json['exc_name']
            self.assertEqual(exception_name, 'ValueError')

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.get')
    def test_rest_get_fail_with_invalid_timestamp_range(self, mock_influx_get):
        """Test fail case in rest_get with an invalid timestamp range."""
        namespace = ('kronos.telemetry.switches.1.interfaces.232.'
                     'bytes_in.12')
        start = 22222
        end = 11111

        mock_influx_get.side_effect = ValueError()

        app = Flask(__name__)
        with app.app_context():
            response = self.napp.rest_get(namespace, start, end)
            exception_name = response.json['exc_name']
            self.assertEqual(exception_name, 'ValueError')

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.save')
    def test_event_save_success_with_influx(self, mock_influx_save):
        """Test success in method event_save."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        value = '123'
        timestamp = None

        event = mock.MagicMock()
        event.content = {'namespace': namespace,
                         'value': value,
                         'timestamp': timestamp}

        self.napp.event_save(event)
        mock_influx_save.assert_called_with(namespace, value, timestamp)

    @mock.patch('napps.kytos.kronos.main.Main._execute_callback')
    @mock.patch('napps.kytos.kronos.main.InfluxBackend.save')
    def test_event_save_fail_with_invalid_namespace(self, mock_influx_save,
                                                    mock_callback):
        """Test fail case in method event_save with an invalid namespace."""
        namespace = 'telemetry.switches.1.interfaces.232.bytes_in'
        value = '123'
        timestamp = None

        event = mock.MagicMock()
        event.content = {'namespace': namespace,
                         'value': value,
                         'timestamp': timestamp}

        # Values expected to call '_execute_callback'
        exc = NamespaceError()
        error = (exc.__class__.__name__, str(exc))
        result = None

        # Set a exception to mocked function return value
        mock_influx_save.side_effect = NamespaceError()

        self.napp.event_save(event)
        mock_callback.assert_called_with(event, result, error)

    @mock.patch('napps.kytos.kronos.main.Main._execute_callback')
    @mock.patch('napps.kytos.kronos.main.InfluxBackend.save')
    def test_event_save_failed_converting_value(self, mock_influx_save,
                                                mock_callback):
        """Test fail case in method rest_save with an invalid value."""
        namespace = 'kytos.telemetry.switches.1.interfaces.232.bytes_in'
        value = '123'
        timestamp = 'abc'

        event = mock.MagicMock()
        event.content = {'namespace': namespace,
                         'value': value,
                         'timestamp': timestamp}

        # Values expected to call '_execute_callback'
        exc = ValueError()
        error = (exc.__class__.__name__, str(exc))
        result = None

        # Set a exception to mocked function return value
        mock_influx_save.side_effect = ValueError()

        self.napp.event_save(event)
        mock_callback.assert_called_with(event, result, error)

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.get')
    def test_event_get_success_with_influx(self, mock_influx_get):
        """Test success in method event_get."""
        namespace = ('kytos.kronos.telemetry.switches.1.interfaces.232.'
                     'bytes_in.12')
        start = 123456
        end = 123457

        mock_influx_get.return_value = [['1970-01-01T00:00:00.001234567Z', 12]]

        event = mock.MagicMock()
        event.content = {'namespace': namespace,
                         'start': start,
                         'end': end}

        self.napp.event_get(event)
        mock_influx_get.assert_called_with(namespace, start, end)

    @mock.patch('napps.kytos.kronos.main.Main._execute_callback')
    @mock.patch('napps.kytos.kronos.main.InfluxBackend.get')
    def test_event_get_fail_with_invalid_namespace(self, mock_influx_get,
                                                   mock_callback):
        """Test fail case in method event_get with an invalid namespace."""
        namespace = 'telemetry.switches.1.interfaces.232.bytes_in'
        start = 123456
        end = 123457

        event = mock.MagicMock()
        event.content = {'namespace': namespace,
                         'start': start,
                         'end': end}

        # Values expected to call '_execute_callback'
        exc = NamespaceError()
        error = (exc.__class__.__name__, str(exc))
        result = None

        # Set a exception to mocked function return value
        mock_influx_get.side_effect = NamespaceError()

        self.napp.event_get(event)
        mock_callback.assert_called_with(event, result, error)

    @mock.patch('napps.kytos.kronos.main.Main._execute_callback')
    @mock.patch('napps.kytos.kronos.main.InfluxBackend.get')
    def test_event_get_fail_with_invalid_timestamp(self, mock_influx_get,
                                                   mock_callback):
        """Test fail case in method event_get with an invalid value."""
        namespace = ('kronos.telemetry.switches.1.interfaces.232.'
                     'bytes_in.12')
        start = 'abc'
        end = 22222

        event = mock.MagicMock()
        event.content = {'namespace': namespace,
                         'start': start,
                         'end': end}

        # Values expected to call '_execute_callback'
        exc = ValueError()
        error = (exc.__class__.__name__, str(exc))
        result = None

        # Set a exception to mocked function return value
        mock_influx_get.side_effect = ValueError()

        self.napp.event_get(event)
        mock_callback.assert_called_with(event, result, error)

    @mock.patch('napps.kytos.kronos.main.Main._execute_callback')
    @mock.patch('napps.kytos.kronos.main.InfluxBackend.get')
    def test_event_get_fail_with_invalid_timestamp_range(self, mock_influx_get,
                                                         mock_callback):
        """Test fail case in method event_get with an invalid value."""
        namespace = ('kronos.telemetry.switches.1.interfaces.232.'
                     'bytes_in.12')
        start = 22222
        end = 11111

        event = mock.MagicMock()
        event.content = {'namespace': namespace,
                         'start': start,
                         'end': end}

        # Values expected to call '_execute_callback'
        exc = ValueError()
        error = (exc.__class__.__name__, str(exc))
        result = None

        # Set a exception to mocked function return value
        mock_influx_get.side_effect = ValueError()

        self.napp.event_get(event)
        mock_callback.assert_called_with(event, result, error)

    @mock.patch('napps.kytos.kronos.main.InfluxBackend.delete')
    def test_event_delete_success_with_influx(self, mock_influx_delete):
        """Test success in method event_delete."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        start = 123456
        end = 123457

        event = mock.MagicMock()
        event.content = {'namespace': namespace,
                         'start': start,
                         'end': end}

        self.napp.event_delete(event)
        mock_influx_delete.assert_called_with(namespace, start, end)

    @mock.patch('napps.kytos.kronos.main.Main._execute_callback')
    @mock.patch('napps.kytos.kronos.main.InfluxBackend.delete')
    def test_event_delete_failed_namespace_wrong_prefix(self, mock_influx_del,
                                                        mock_callback):
        """Test fail case in method event_delete with an invalid namespace."""
        namespace = 'telemetry.switches.1.interfaces.232.bytes_in'
        start = 123456
        end = 123457

        event = mock.MagicMock()
        event.content = {'namespace': namespace,
                         'start': start,
                         'end': end}

        # Values expected to call '_execute_callback'
        exc = NamespaceError()
        error = (exc.__class__.__name__, str(exc))
        result = None

        # Set a exception to mocked function return value
        mock_influx_del.side_effect = NamespaceError()

        self.napp.event_delete(event)
        mock_callback.assert_called_with(event, result, error)

    @mock.patch('napps.kytos.kronos.main.Main._execute_callback')
    @mock.patch('napps.kytos.kronos.main.InfluxBackend.delete')
    def test_event_delete_fail_invalid_timestamp(self, mock_influx_del,
                                                 mock_callback):
        """Test fail case in method rest_delete with an invalid timestamp."""
        namespace = 'kytos.telemetry.switches.1.interfaces.232.bytes_in'

        start = 'abc'
        end = 22222

        event = mock.MagicMock()
        event.content = {'namespace': namespace,
                         'start': start,
                         'end': end}

        # Values expected to call '_execute_callback'
        exc = ValueError()
        error = (exc.__class__.__name__, str(exc))
        result = None

        # Set a exception to mocked function return value
        mock_influx_del.side_effect = ValueError()

        self.napp.event_delete(event)
        mock_callback.assert_called_with(event, result, error)
