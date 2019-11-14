"""Module to test the main napp file."""
import logging
import pandas as pd
import time
from unittest import TestCase
from unittest.mock import MagicMock, Mock

from napps.kytos.kronos.backends.csvbackend import CSVBackend
from napps.kytos.kronos.utils import now
from napps.kytos.kronos import settings
from kytos.core.link import Link
from tests.helpers import get_controller_mock


logging.basicConfig(level=logging.CRITICAL)


class Test_CSVBackend(TestCase):
    """Test methods in CSV Backend."""
            
    def test_save_success(self):
        '''Test to check the success in data storage in CSV Backend.'''
        namespace = 'kytos.telemetry.switches.1.interfaces.232.bytes_in'
        value = '1324'
        timestamp = now()

        result = CSVBackend(settings).save(namespace, value, timestamp)

        self.assertEqual(None, result)

    def test_get_success(self):
        '''Test to check success in data retrieving in CSV Backend.'''
        
        '''Saving data to guarantee that data exists.'''
        namespace = 'kytos.telemetry.switches.1.interfaces.232.bytes_in'
        value = '1324'
        timestamp = now()

        csvbackend = CSVBackend(settings)
        csvbackend.save(namespace, value, timestamp)

        '''Testing the get method'''
        f_name = csvbackend.user + '_' + namespace + '.csv'
       
        result = csvbackend.get(f_name, start=timestamp)
        
        expected_store_value = pd.DataFrame(columns=['Value', 'Timestamp'])
        expected_store_value.loc[0, 'Value'] = value
        expected_store_value.loc[0, 'Timestamp'] = timestamp
        
        pd.util.testing.assert_frame_equal(expected_store_value, result)


