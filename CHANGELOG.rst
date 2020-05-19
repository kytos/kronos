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


[0.9] - 2020-04-19
****************************************

Added
=====
 - Added failure and success test cases to main and utils modules.

Changed
=======
 - Replace kytos/kronos specific exception TimestampRangeError by a ValueError.
 - Refactor methods of main and utils to return values and handle exceptions.

[0.8] - 2020-04-02
****************************************

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
