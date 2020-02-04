"""Tests main module of kytos/kronos."""
import sys 
from flask import Flask
from unittest import TestCase, mock

sys.modules['influxdb'] = mock.MagicMock()

from kytos.core import KytosNApp
from napps.kytos.kronos.main import Main
from tests.helpers import get_controller_mock

class TestMainKronos(TestCase):
    """Class to test kytos/kronos."""
    def setUp(self):
        self.napp = Main(get_controller_mock())

    @mock.patch('main.Main.backend')
    def test_restsave_success(self, mock_main):
        """Test succes in method rest_save."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        value = '123'
        
        app = Flask(__name__)
        with app.app_context():
            self.napp.rest_save(namespace, value)
            mock_main.save.assert_called_with(namespace, value)
