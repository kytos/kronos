"""Tests main module of kytos/kronos."""
from unittest import TestCase, mock

from kytos.core import KytosNApp
from napps.kytos.kronos.main import Main


class TestMainKronos(TestCase):
    """Class to test kytos/kronos."""

    @mock.patch('main.Main')
    def test_restsave_success(self, mock_main):
        """Test succes in method rest_save."""
        namespace = 'kytos.kronos.telemetry.switches.1.interfaces.232.bytes_in'
        value = '123'

        main = Main(KytosNApp)

        mock_main.backend.save(namespace, value).return_value = None

        result = main.backend.save(namespace, value)

        self.assertEqual(None, result)
