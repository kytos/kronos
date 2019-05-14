"""Backend that save data along time using a csv file"""
import os

import pandas as pd

from napps.kytos.kronos.utils import (validate_timestamp, now,
                                       iso_format_validation)


def _put_value(value, store_value, timestamp=None):
    """Save a value in a dataframe."""
    store_value.loc[0, 'Value'] = value
    store_value.loc[0, 'Timestamp'] = timestamp or now()


def _config_path(file_path):

    if file_path is None:
        if 'data' not in os.listdir():
            os.system('mkdir data')
        file_path = 'data/'
    else:
        if file_path == '':
            file_path = '/'
        elif file_path[-1] != '/':
            file_path = file_path + '/'
        try:
            os.listdir(file_path)
        except (FileNotFoundError, IOError):
            raise Exception("Invalid File or Directory:{}" .format(file_path))

    return file_path


def _make_search(start, end, dataframe):
    '''Return part of the dataframe'''
    end = end or now()
    start = start or 0

    validate_timestamp(start, end)
    start = iso_format_validation(start)
    end = iso_format_validation(end)

    iso = '%Y-%m-%dT%H:%M:%SZ'
    search = dataframe.Timestamp.dt.strftime(iso)
    search = search.between(start, end)

    return search


class CSVBackend:
    """CSV backend class. Defines methods to save,
    retrieve and delete data along time."""

    def __init__(self, settings):
        """Define the a path in case the user does not pass one.
        Also defines the user getting from the backend."""
        self._read_config(settings)

    def _read_config(self, settings):
        params = {'PATH': None, 'USER': 'default_user'}
        config = settings.BACKENDS.get('CSV')
        for key in params:
            params[key] = config.get(key, params[key])

        self.path = _config_path(params['PATH'])
        self.user = params['USER']

    def save(self, namespace, value, timestamp=None):
        """ Store the data in a .csv given a folder. """
        store_value = pd.DataFrame(columns=['Value', 'Timestamp'])
        _put_value(value, store_value, timestamp)

        f_name = self.user + '_' + namespace + '.csv'
        if self.path != '/':
            f_name = self.path + f_name

        if f_name in os.listdir(self.path):
            store_value.to_csv(f_name, sep=',', header=False,
                               mode='a', index=False)
        else:
            store_value.to_csv(f_name, sep=',', header=True,
                               mode='w', index=False)

    def delete(self, file, start=None, end=None):
        """ Delete a instances of the csv file"""
        dataframe, file = self._load_file(file)
        search = _make_search(start, end, dataframe)
        data_to_drop = dataframe[search]
        dataframe.drop(data_to_drop.index, inplace=True)
        if self.path != '/':
            file = self.path + file

        dataframe.to_csv(file, sep=',', header=True, mode='w', index=False)

    def get(self, file, start=None, end=None, method=None,
            fill=None, group=None):
        """Retrieve data from a csv file"""
        dataframe, file = self._load_file(file)
        search = _make_search(start, end, dataframe)

        return dataframe[search]

    def _load_file(self, file):
        """load the file passing the name + the path."""
        try:
            if '.csv' not in file:
                file = file + '.csv'

            if self.path != '/':
                file = self.path + file

            dataframe = pd.read_csv(file, sep=',')
            dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'],
                                                    errors='coerce')
            return dataframe, file

        except (FileNotFoundError, IOError):
            raise Exception("File Not Found")
