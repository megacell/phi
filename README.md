Installation
============
Python
------
We are currently running python 2.7 on all systems. We try our best to stay up
to date on the latest security patches.

We use the following python libraries (most of these can, and probably should,
be installed via pip):
- [django](https://www.djangoproject.com/) (specifically the geodjango library)
- [requests](http://docs.python-requests.org/en/latest/)
- [pico](https://github.com/fergalwalsh/pico)

Postgres
--------
The database that we are slowly migrating towards is postgres. The installation
instructions for this vary from system to system. If you find a good one for
your system, link to it here.

We will also be using [*postgis*](http://postgis.net/) extensions for geometry
support in postrges.  This has already been installed on the server. For me,
on Linux, my package manager had postgis, so it was fairly simple. Hopefully
this is true for brew, etc.

Geos
----
If this does not come by default with postgis, you will probably need
[geos](http://trac.osgeo.org/geos/) as well. TBH, I don't remember exactly
where this dependency comes in to the system. If you discover where this is
required, please update the README.

Database Schema
===============
Details on how we are going to lay this out to come.

Sensors
=======
Required to have following columns:
- Latitude
- Longitude
