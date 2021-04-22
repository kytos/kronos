#########
Changelog
#########

All notable changes to the ``kronos`` project will be documented in this file.

[UNRELEASED] - Under development
********************************
Added
=====

Changed
=======

Deprecated
==========

Removed
=======

Fixed
=====

Security
========

Changed
=======


[1.1] - 2021-04-22
******************

Added
=====
- Added support to influx backend save a dictionary. This modification
  reduces the number of events received from NApp ``kytos/of_stats``.

Changed
=======
- Replace ``ValueConvertError`` by ``ValueError`` Python exception.

Fixed
=====
- Adjusted the main module to only import the InfluxDB backend module when
  this backend is set in ``settings.py``.
- Increase the connection pool size of InfluxDB client to remove warnings.


[1.0] - 2020-07-07
******************

Added
=====
 - Added failure and success test cases to main and utils modules.
 - Added ``@tags`` decorator to run tests by type and size.

Changed
=======
 - Replace kytos/kronos specific exception TimestampRangeError by a ValueError.
 - Refactor methods of main and utils to return values and handle exceptions.
 - Refactor InfluxDB backend tests.

[0.8] - 2020-04-02
******************

Added
=====
 - Added CSV backend to proof of concept for kronos with save, get and delete 
   methods.
 - Added InfluxDB backend to enable to store times series data with 
   save, get and delete methods.  
 - Added Kytos events in main.py.
 - Added REST endpoints in main.py. 

Changed
=======

Deprecated
==========

Removed
=======

Fixed
=====

Security
========
