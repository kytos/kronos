"""Module with the Constants used in the kytos/Kronos."""

DEFAULT_BACKEND = 'INFLUXDB'
BACKENDS = {}
BACKENDS['INFLUXDB'] = {
    'USER': 'foo',
    'PASS': 'bar',
    'PORT': 8086,
    'HOST': 'localhost',
    'DBNAME': 'kytos',
    'POOL_SIZE': 100
}
BACKENDS['CSV'] = {
    'USER': 'foo',
    'PATH': 'data/'
}
