"""InfluxDB backend."""
import re

from influxdb import InfluxDBClient, exceptions
from kytos.core import log

from napps.kytos.kronos.utils import (iso_format_validation, now,
                                      validate_timestamp)


def _query_assemble(clause, namespace, start, end, field=None,
                    method=None, group=None, fill=None):

    if clause.upper() == 'SELECT':
        if field is None:
            clause += f' * FROM {namespace}'
        else:
            if method is None:
                clause += f" {field} FROM {namespace}"
            else:
                clause += f" {method}({field}) FROM {namespace}"

    elif clause.upper() == 'DELETE':
        clause += f' FROM {namespace}'
    else:
        log.error(f'Error. Invalid clause "{clause}".')

    time_clause = " WHERE time "
    if start is not None:
        clause += f"{time_clause} >'{str(start)}'"
        if end is not None:
            clause += f" AND time <'{str(end)}'"
    elif start is None and end is not None:
        clause += f"{time_clause} < '{str(end)}'"

    if group is not None:
        clause += f" GROUP BY time({group})"
    if fill is not None:
        clause += f" fill({fill})"

    return clause


def _verify_namespace(namespace):
    field = None

    if namespace is None:
        log.error("Error. Namespace cannot be NoneType.")
        return 400, 400

    if not isinstance(namespace, str) or not re.match(r'\S+', namespace):
        log.error(f"Error. Namespace '{namespace}' most be a string."
                  f" Not {type(namespace).__name__}.")
        return 404, 404

    if '.' in namespace:
        field = namespace.split('.')[-1]
        namespace = '.'.join(namespace.split('.')[:-1])
    return namespace, field

def _parse_result_set(result, field):

    if result:
        time_value, value = zip(*[(res['time'],
                                res[field]) for res in list(result)[0]])

        return (time_value, value)

    return None

class InvalidQuery(Exception):
    """Exception thrown when the assembled query is not valid."""


class InfluxBackend:
    """This Backend is responsible to the connection with InfluxDB."""

    def __init__(self, settings):
        """Read config and start client."""
        self._read_config(settings)
        self._start_client()

    def save(self, namespace, value, timestamp=None):
        """Insert the data on influxdb.

        In this case (InfluxDB), the last namespace will be the table.

        timestamp must be on ISO-8601 format.
        """
        if re.match(r'[+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', value):
            value = float(value)
        elif not isinstance(value, bool) and isinstance(value, int):
            value = float(value)

        timestamp = timestamp or now()
        timestamp = iso_format_validation(timestamp)
        if timestamp == 400:
            return timestamp

        namespace, field = _verify_namespace(namespace)
        if isinstance(namespace, tuple):
            namespace = namespace[0]
        if namespace in (400, 404):
            return namespace

        data = [{
            'measurement': namespace,
            'time': timestamp,
            'fields': {field: value}
        }]

        return self._write_endpoints(data)

    def delete(self, namespace, start=None, end=None):
        """Delete the entire database.

        start and end most be a timestamp
        """
        start = iso_format_validation(start)
        end = iso_format_validation(end)
        namespace = _verify_namespace(namespace)
        if isinstance(namespace, tuple):
            namespace = namespace[0]

        if namespace in (400, 404):
            return namespace

        if not self._namespace_exists(namespace):
            log.error("Namespace {} does not exist".format(namespace))
            return 400

        if validate_timestamp(start, end) == 400:
            return 400

        self._delete_points(namespace, start, end)
        return 200

    def get(self, namespace, start=None, end=None,
            method=None, fill=None, group=None):
        """Make a query to retrieve something in the database."""
        start = iso_format_validation(start)
        end = iso_format_validation(end)
        namespace, field = _verify_namespace(namespace)
        if not self._namespace_exists(namespace):
            return 400
        if validate_timestamp(start, end) == 400:
            return 400
        points = self._get_points(namespace, start, end,
                                  field, method, fill, group)
        return _parse_result_set(points, field)

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
            log.error("Error. Must specify database name.")

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
            return 400
        except InvalidQuery:
            log.error("Error inserting data to InfluxDB.")
            return 400

        return 200

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
            return self._client.query(query, chunked=True, chunk_size=0)
        except InvalidQuery:
            log.error("Error. Query {} not valid" .format(query))
            return 400

    def _namespace_exists(self, namespace):

        if namespace is None:
            log.error("Invalid namespace.")
            return 400

        all_nspace = self._client.get_list_measurements()
        if not all_nspace:
            log.error("Error. There are no valid database.")
            return 400
        exist = list(filter(lambda x: x['name'] == namespace, all_nspace))
        if not exist:
            log.error("Required namespace does not exist.")
            return 400

        return True
