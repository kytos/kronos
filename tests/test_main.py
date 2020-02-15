"""Tests main module of kytos/kronos."""
from flask import Flask
from tests.helpers import get_controller_mock

from napps.kytos.kronos.utils import InvalidNamespaceError

# pylint: disable=wrong-import-order,wrong-import-position
import sys
from unittest import TestCase, mock
sys.modules['influxdb'] = mock.MagicMock()
from napps.kytos.kronos.main import Main
# pylint: enable=wrong-import-order,wrong-import-position


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
        """Test a error in method rest_save passing an invalid namespace."""
        namespace = 'telemetry.switches.1.interfaces.232.bytes_in'
        value = '123'
        timestamp = None

        mock_influx_save.side_effect = InvalidNamespaceError()

        app = Flask(__name__)
        with app.app_context():
            response = self.napp.rest_save(namespace, value, timestamp)
            exception_name = response.json['exc_name']
            self.assertEqual(exception_name, 'InvalidNamespaceError')
