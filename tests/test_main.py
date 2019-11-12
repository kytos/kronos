"""Module to test the main napp file."""
import logging
import time
from unittest import TestCase
from unittest.mock import MagicMock

from napps.kytos.kronos.main import Main
from kytos.core.link import Link

logging.basicConfig(level=logging.CRITICAL)


class TestMain(TestCase):
    """Test Links."""

    def test_event_save(self):
       
        mock_main = Main()
        
        mock_main.backend.save = MagicMock(return_value=200)
        
        self.assertEqual(main.event_save(), 200)
        
    
