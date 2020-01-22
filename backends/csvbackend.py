"""Backend that save data along time using a csv file."""
import csv
import os
from pathlib import Path

from napps.kytos.kronos.utils import (iso_format_validation, now,
                                      validate_timestamp)


def _config_path(file_path):

    if not Path(file_path).exists:
        path = Path(file_path)
        path.mkdir(parents=True)
        file_path = str(path)
    elif file_path == '':
        file_path = '/'
    else:
        file_path = str(Path(file_path))

    return file_path


def _make_search(start, end, fname):
    """Return the result of the search in csv file."""
    end = end or now()
    start = start or 0

    validate_timestamp(start, end)
    start = iso_format_validation(start)
    end = iso_format_validation(end)

    search = []

    with open(fname, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            if start <= row[1] <= end:
                search.append(row)
    return search


class CSVBackend:
    """CSV backend class defines methods to store, retrieve and delete data."""

    def __init__(self, settings):
        """Define the user and a path in case the user does not pass one."""
        self._read_config(settings)

    def _read_config(self, settings):
        params = {'PATH': 'data', 'USER': 'default_user'}
        config = settings.BACKENDS.get('CSV')
        for key in params:
            params[key] = config.get(key, params[key])

        self.path = _config_path(params['PATH'])
        self.user = params['USER']

    def save(self, namespace, value, timestamp=None):
        """Store the data in a .csv given a folder."""
        rows = []

        fname = f"{self.user}_{namespace}.csv"
        fname = str(Path(self.path, fname))

        if not os.path.exists(fname):
            rows.append(['Value', 'Timestamp'])

        rows.append([value, timestamp])

        csvfile = open(fname, 'a', newline='')

        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerows(rows)
        csvfile.close()

    def delete(self, namespace, fname, start=None, end=None):
        """Delete a instances of the csv file."""
        fname = f"{self.user}_{namespace}.csv"
        fname = str(Path(self.path, fname))

        search = _make_search(start, end, fname)

        result = []

        with open(fname, 'r+', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')

            for row in csvreader:
                if row not in search:
                    result.append(row)

            csvwriter = csv.writer(csvfile, delimiter=',')

            for row in result:
                csvwriter.writerow(row)

        csvfile.close()

    def get(self, namespace, fname, start=None, end=None, method=None,
            fill=None, group=None):
        """Retrieve data from a csv file."""
        fname = f"{self.user}_{namespace}.csv"
        fname = str(Path(self.path, fname))

        search = _make_search(start, end, fname)

        return search
