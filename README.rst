########
Overview
########

Attention!

THIS IS AN EXPERIMENTAL NAPP AND ITS EVENTS, METHODS AND STRUCTURES MAY CHANGE A LOT ON THE NEXT FEW DAYS/WEEKS, USE IT AT YOUR OWN DISCERNMENT

The Kronos NApp is responsible for data persistence, saving and retrieving information from time series database (TSDB). It can be acessed by external agents through the REST API or by other NApps, using the event-based methods.

The data can be saved in a different namespace, with support for nested namespaces.

The NApp is designed to support many options of back-end persistence solutions. Currently the InfluxDB backend is under development, but alternatives for other TSDB can be implemented in the future.

##########
Installing
##########

All of the Kytos Network Applications are located in the NApps online repository.
To install this NApp, run:

.. code:: shell

   $ kytos napps install kytos/kronos

###########
Configuring
###########

Settings are stored in the ``settings.py``file. The options there may be different according to the backend you are using. For example, the ``InfluxDB`` backend will use ``PORT``, ``PASS``, ``HOST`` and ``DBNAME``, while ``CSVBackend`` will just ignore those.

######
Events
######

The NApp listens to events requesting operations. Every event must have a callback function to be executed right after the internal method returns. The signature of the callback function is described with each event.

kytos.kronos.save
=================
Event requesting to save data in a namespace from backend.

kytos.kronos.get
================
Event requesting data in a namespace from backend.

kytos.kronos.delete
===================
Event requesting to delete data in a namespace from backend.


