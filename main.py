"""Main module of kytos/Cronos Kytos Network Application.

Napp to store itens along time
"""
from flask import jsonify, request
from napps.kytos.kronos import settings
from napps.kytos.kronos.backends.csvbackend import CSVBackend
from napps.kytos.kronos.backends.influx import InfluxBackend
from kytos.core import KytosNApp, log, rest


class Main(KytosNApp):
    """Main class of kytos/Cronos NApp.

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
    def save(self, namespace, value, timestamp=None):
        """Save the data in one of the backends."""
        result = self.backend.save(namespace, value, timestamp)
        if result in (400, 404):
            return jsonify({"response": "Not Found"}), result

        return jsonify({"response": "Value saved !"}), 201

    @rest('v1/<namespace>/', methods=['DELETE'])
    @rest('v1/<namespace>/start/<start>', methods=['DELETE'])
    @rest('v1/<namespace>/end/<end>', methods=['DELETE'])
    @rest('v1/<namespace>/<start>/<end>', methods=['DELETE'])
    def delete(self, namespace, start=None, end=None):
        """Delete the data in one of the backends."""
        result = self.backend.delete(namespace, start, end)
        if result in (400, 404):
            return jsonify({"response": "Not Found"}), 404

        return jsonify({"response": "Values deleted !"}), 200


    @rest('v1/<namespace>', methods=['GET']) # /teste2.out/?start=0&end=100000
    def get(self, namespace, start=None, end=None, method=None,
            fill=None, group=None):
        """Retrieve the data from one of the backends."""
        start = request.args.get('start')
        end = request.args.get('end')
        result = self.backend.get(namespace, start, end, method, fill, group)
        if result == 400 or result is None:
            return jsonify({"response": 'Not Found'}), 404

        elif isinstance(result, tuple):  # time, value, code
            return jsonify({"response": (result[0], result[1])}), 200

        return jsonify(result), 200

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
