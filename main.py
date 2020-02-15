"""Main module of kytos/Cronos Kytos Network Application.

Napp to store itens along time
"""
from flask import jsonify

from kytos.core import KytosNApp, log, rest
from kytos.core.helpers import listen_to
from napps.kytos.kronos import settings
from napps.kytos.kronos.backends.csvbackend import CSVBackend
from napps.kytos.kronos.backends.influx import InfluxBackend
from napps.kytos.kronos.utils import InvalidNamespaceError, ValueConvertError


class Main(KytosNApp):
    """Main class of kytos/kronos NApp.

    This class is the entry point for this napp.
    """

    backend = None

    def setup(self):
        """Init method for the napp."""
        log.info("Time Series NApp started.")

        if settings.DEFAULT_BACKEND == 'INFLUXDB':
            self.backend = InfluxBackend(settings)
        elif settings.DEFAULT_BACKEND == 'CSV':
            self.backend = CSVBackend(settings)

    @rest('v1/<namespace>/<value>', methods=['POST'])
    @rest('v1/<namespace>/<value>/<timestamp>', methods=['POST'])
    def rest_save(self, namespace, value, timestamp=None):
        """Save the data in one of the backends."""
        try:
            self.backend.save(namespace, value, timestamp)
        except (InvalidNamespaceError, ValueConvertError) as exc:
            exc_name = exc.__class__.__name__
            return jsonify({'response': str(exc), 'exc_name': exc_name})

        return jsonify({'response': 'Value saved !'})

    @rest('v1/<namespace>/', methods=['DELETE'])
    @rest('v1/<namespace>/start/<start>', methods=['DELETE'])
    @rest('v1/<namespace>/end/<end>', methods=['DELETE'])
    @rest('v1/<namespace>/<start>/<end>', methods=['DELETE'])
    def rest_delete(self, namespace, start=None, end=None):
        """Delete the data in one of the backends."""
        log.info(start)
        log.info(end)
        result = self.backend.delete(namespace, start, end)
        if result in (400, 404):
            return jsonify({"response": "Not Found"}), 404

        return jsonify({"response": "Values deleted !"}), 200

    @rest('v1/namespace/', methods=['GET'])
    @rest('v1/<namespace>/', methods=['GET'])
    @rest('v1/<namespace>/<start>/', methods=['GET'])
    @rest('v1/<namespace>/<end>/', methods=['GET'])
    @rest('v1/<namespace>/<start>/<end>', methods=['GET'])
    @rest('v1/<namespace>/<start>/<end>/interpol/<method>', methods=['GET'])
    @rest('v1/<namespace>/<start>/<end>/interpol/<method>/<filter>/',
          methods=['GET'])
    @rest('v1/<namespace>/<start>/<end>/interpol/<method>/<filter>/<group>',
          methods=['GET'])
    def rest_get(self, namespace, start=None, end=None, method=None,
                 fill=None, group=None):
        """Retrieve the data from one of the backends."""
        result = self.backend.get(namespace, start, end, method, fill, group)
        if result == 400 or result is None:
            return jsonify({"response": 'Not Found'}), 404

        return jsonify({"response": result}), 200

    @listen_to('kytos.kronos.save')
    def event_save(self, event):
        """Save the data in one of the backends."""
        try:
            self.backend.save(event.content['namespace'],
                              event.content['value'],
                              event.content['timestamp'])
        except Exception as exc:
            result = None
            error = (exc.__class__, exc.args)

        self._execute_callback(event, result, error)

    @listen_to('kytos.kronos.get')
    def event_get(self, event):
        """Get the data in one of the backends."""
        try:
            self.backend.get(event.content['namespace'],
                             event.content['timestamp'])
        except Exception as exc:
            result = None
            error = (exc.__class__, exc.args)

        self._execute_callback(event, result, error)

    @listen_to('kytos.kronos.delete')
    def event_delete(self, event):
        """Delete data in one of the backends."""
        try:
            self.backend.delete(event.content['namespace'],
                                event.content['timestamp'])
        except Exception as exc:
            result = None
            error = (exc.__class__, exc.args)

        self._execute_callback(event, result, error)

    @staticmethod
    def _execute_callback(event, data, error):
        """Run the callback function for event calls to the NApp."""
        try:
            event.content['callback'](event, data, error)
        except KeyError:
            log.error(f'Event {event} without callback function!')
        except TypeError as exception:
            log.error(f'Bad callback function {event.content["callback"]}!')
            log.error(exception)

    def execute(self):
        """Run after the setup method execution.

        You can also use this method in loop mode if you add to the above setup
        method a line like the following example:

            self.execute_as_loop(30)  # 30-second interval.
        """
        log.info("EXECUTING !")

    def shutdown(self):
        """Execute before tha NApp is unloaded."""
        log.info("Time Series NApp is shutting down.")
