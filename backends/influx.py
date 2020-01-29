"""InfluxDB backend."""
import re

from influxdb import InfluxDBClient, exceptions

from kytos.core import log
from napps.kytos.kronos.utils import (InvalidNamespaceError,
                                      NamespaceNotExistsError,
                                      TimestampRangeError, ValueConvertError,
                                      convert_to_iso, iso_format_validation,
                                      now, validate_timestamp)


def _query_assemble(clause, namespace, start, end, field=None,
                    method=None, group=None, fill=None):

    if clause.upper() == 'SELECT':
        if field is None:
            clause += f' * FROM {namespace}'
        else:
            if method is None:
                clause += f' {field} FROM "{namespace}"'
            else:
                clause += f' {method}({field}) FROM "{namespace}"'

    elif clause.upper() == 'DELETE':
        clause += f' FROM "{namespace}"'
    else:
        log.error(f'Error. Invalid clause "{clause}".')

    time_clause = ' WHERE time '
    if start is not None:
        clause += f'{time_clause} >= \'{str(start)}\''
        if end is not None:
            clause += f' AND time <=\'{str(end)}\''
    elif start is None and end is not None:
        clause += f'{time_clause} <= \'{str(end)}\''

    if group is not None:
        clause += f' GROUP BY time({group})'
    if fill is not None:
        clause += f' fill({fill})'
    return clause


def _validate_namespace(namespace):
    if not isinstance(namespace, str) or not re.match(r'\S+', namespace):
        error = (f'Error. Namespace should be a string.')
        raise TypeError

    if 'kytos.kronos' not in namespace:
        error = (f'Error. Namespace \'{namespace}\' most have the format '
                 '\'kytos.kronos.*\'')
        raise InvalidNamespaceError(error)

    return True


def _extract_field(namespace):
    field = namespace.split('.')[-1]
    namespace = '.'.join(namespace.split('.')[:-1])
    return namespace, field


class InvalidQuery(Exception):
    """Exception thrown when the assembled query is not valid."""


class InfluxBackend:
    """This Backend is responsible to the connection with InfluxDB."""

    def __init__(self, settings):
        """Read config from settings file and start a InfluxBackend client."""
        self._read_config(settings)
        self._start_client()

    def save(self, namespace, value, timestamp=None):
        """Insert data on influxdb."""
        if _validate_namespace(namespace):
            namespace, field = _extract_field(namespace)

        try:
            value = float(value)
        except ValueError:
            error = f'Is not possible convert value \'{value}\' to float.'
            raise ValueConvertError(error)

        timestamp = timestamp or now()
        if iso_format_validation(timestamp) is False:
            timestamp = convert_to_iso(timestamp)

        data = [{
            'measurement': namespace,
            'time': timestamp,
            'fields': {field: value}
        }]

        return self._write_endpoints(data)

    def get(self, namespace, start=None, end=None,
            method=None, fill=None, group=None):
        """Make a query to retrieve something in the database."""
        if _validate_namespace(namespace):
            namespace, field = _extract_field(namespace)

        if not self._namespace_exists(namespace):
            error = (f'Error to get values because namespace \'{namespace}\''
                     'does not exist.')
            raise NamespaceNotExistsError(error)

        if start is None and end is None:
            error = 'Start and end value should not be \'None\'.'
            raise ValueError(error)

        if iso_format_validation(start) is False and start is not None:
            start = convert_to_iso(start)
        if iso_format_validation(end) is False and end is not None:
            end = convert_to_iso(end)

        if validate_timestamp(start, end) is False:
            error = 'Error to get values due end value is smaller than start.'
            raise TimestampRangeError(error)

        points = self._get_points(namespace, start, end,
                                  field, method, fill, group)
        return points

    def delete(self, namespace, start=None, end=None):
        """Delete data in influxdb. Start and end most be a timestamp."""
        if iso_format_validation(start) is False and start is not None:
            start = convert_to_iso(start)
        if iso_format_validation(end) is False and end is not None:
            end = convert_to_iso(end)

        if _validate_namespace(namespace):
            namespace, _ = _extract_field(namespace)
        else:
            log.error('Error in delete method due invalid namespace value.')
            return

        if not self._namespace_exists(namespace):
            log.error(f'Error to delete because namespace \'{namespace}\' does'
                      'not exist.')
            return

        if validate_timestamp(start, end) is False:
            log.error('Error to delete due invalid namespace')
            return

        self._delete_points(namespace, start, end)
        return

    def _read_config(self, settings):

        params = {'HOST': 'localhost',
                  'PORT': '8086',
                  'DBNAME': None,
                  'USER': None,
                  'PASS': None}
        config = settings.BACKENDS.get('INFLUXDB')

        for key in params:
            params[key] = config.get(key, params[key])

        if not params['DBNAME']:
            log.error('Error. Must specify database name.')

        self._host = params['HOST']
        self._port = params['PORT']
        self._username = params['USER']
        self._password = params['PASS']
        self._database = params['DBNAME']

    def _start_client(self):
        self._client = InfluxDBClient(host=self._host,
                                      port=self._port,
                                      username=self._username,
                                      password=self._password,
                                      database=self._database)

    def _create_database(self):
        self._client.create_database(self._database)

    def _write_endpoints(self, data, create_database=True):

        if not self._get_database() and create_database:
            self._create_database()

        try:
            self._client.write_points(data)
        except exceptions.InfluxDBClientError as error:
            log.error(error)
        except InvalidQuery:
            log.error('Error inserting data to InfluxDB.')

    def _get_database(self):
        """Verify if a database exists."""
        all_dbs = self._client.get_list_database()
        exist = list(filter(lambda x: x['name'] == self._database, all_dbs))
        if not exist:
            return False

        return True

    def _delete_points(self, namespace, start, end):

        query = _query_assemble('DELETE', namespace, start, end)

        self._client.query(query)

    def _get_points(self, name, start, end,
                    field=None, method=None, fill=None, group=None):

        query = _query_assemble('SELECT', name, start, end, field,
                                method, group, fill)
        try:
            results = self._client.query(query, chunked=True, chunk_size=0).raw
            results = results['series'][0]['values']
            return results
        except KeyError:
            error = (f'Error. Query {query} not valid')
            raise InvalidQuery(error)

    def _namespace_exists(self, namespace):

        if namespace is None:
            log.error('Invalid namespace.')
            return False

        all_nspace = self._client.get_list_measurements()
        if not all_nspace:
            log.error('Error. There are no valid database.')
            return False
        exist = list(filter(lambda x: x['name'] == namespace, all_nspace))
        if not exist:
            log.error('Required namespace does not exist.')
            return False

        return True
