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
- [south](http://south.readthedocs.org/en/latest/installation.html#installation)
  _Make sure to configure properly_
- [psycopg2](http://initd.org/psycopg/)

Installation via pip (confirmed for OSX 10.8):

    sudo easy_install-2.7 pip-2.7
    pip-2.7 install -r requirements.txt

GeoDjango
---------
- [gis](https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/) install
instructions give platform specific instructions for all the packages you need
to get this working.

Postgres **9.3**
----------------
The database that we are slowly migrating towards is postgres. The installation
instructions for this vary from system to system. If you find a good one for
your system, link to it here.

We will also be using [*postgis*](http://postgis.net/) extensions for geometry
support in postrges.  This has already been installed on the server. For me,
on Linux, my package manager had postgis, so it was fairly simple. Hopefully
this is true for brew, etc.

It is important that you use 9.3, because for our sanity we started using
materialized views, a feature only available on this side of the 9.3 line.

I am using the following tutorial to set up models that support postgis-backing:
[Using the Django ORM as a standalone component](https://jystewart.net/2008/02/18/using-the-django-orm-as-a-standalone-component/)

To set up the postgres/postgis database for the megacell project, I did the
following (YMMV):
```bash
su -
su postgres
createdb template_postgis
createlang plpgsql template_postgis
psql -d template_postgis -f /usr/share/postgresql/contrib/postgis-2.1/postgis.sql
psql -d template_postgis -f /usr/share/postgresql/contrib/postgis-2.1/spatial_ref_sys.sql
exit
su - postgres -c 'createdb -T template_postgis geodjango'
su postgres
psql template1
```
In postgres console:
```sql
CREATE USER megacell;
ALTER DATABASE geodjango OWNER TO megacell;
GRANT ALL PRIVILEGES ON DATABASE geodjango TO megacell;
```

Setup for OSX (based on [Instructions for OSX](http://lukeberndt.com/2011/postgres-postgis-on-osx-lion/), confirmed for OSX 10.8)
```bash
initdb /usr/local/var/postgres_mc/
```
Then start the database:
```bash
postgres -D /usr/local/var/postgres_mc/
```
In a separate shell:
```bash
createdb template_postgis
psql -d template_postgis -f /usr/local/share/postgis/postgis.sql
psql -d template_postgis -f /usr/local/share/postgis/spatial_ref_sys.sql
createdb -T template_postgis geodjango
psql template1
```
In postgres console:
```sql
CREATE USER megacell;
ALTER DATABASE geodjango OWNER TO megacell;
GRANT ALL PRIVILEGES ON DATABASE geodjango TO megacell;
```

Geos
----
If this does not come by default with postgis, you will probably need
[geos](http://trac.osgeo.org/geos/) as well. TBH, I don't remember exactly
where this dependency comes in to the system. If you discover where this is
required, please update the README.

Data files
==========
To push changes: 
```bash
rsync -e ssh datasets/Phi --exclude Phi/data -rzv <HOST_URL>:datasets
```

To pull changes: must have an empty (or previously pulled) directory called 
datasets.
```bash
rsync -e ssh --exclude Phi/data -rzv <HOST_URL>:datasets .
```

The first time you pull (if you want the entire dataset), you can remove the 
exclude. That has all of the routes as JSON files. If you don't want them, 
leave the exclude in there. Either way, when you push or pull after the first 
time, you want to exclude that directory.

Database Schema
===============
To start, make sure that the environment is set up properly. Replace BASE_DIR
with the path to the root of this project.
```bash
export PYTHONPATH=$PYTHONPATH:BASE_DIR:BASE_DIR/django_utils
```
To install and update the database schema, go into `/django_utils` and run
```bash
django-admin.py syncdb --settings=settings_geo
django-admin.py migrate --settings=settings_geo
```

Importing data (sensors, origins, routes, and waypoints)
=======
To start, make sure that the environment is set up properly. Replace BASE_DIR
with the path to the root of this project. Make sure you have the entire Phi 
dataset, and all of your migrations are run.
```
export PYTHONPATH=$PYTHONPATH:BASE_DIR:BASE_DIR/django_utils
```
To load the sensors into the database, go to `/djange_utils` and open
`orm/load.py`. Set the file path to the appropriate path on your machine, save
and run `django-admin.py shell --settings=settings_geo`
In the shell, execute
```python
from orm import load
load.import_sensors()
load.load_origins()
load.import_lookup()
load.import_routes()
load.import_waypoints()
```
Some of the commands will take a while to run, in particular importing routes.

Exit the shell, and from the bash prompt in `django_utils` run (these may take
a while too):
```bash
psql -U <SUPERUSER> -d geodjango -f waypoints/voronoi_python.sql
psql -U megacell -d geodjango -f waypoints/set_waypoint_voronoi.sql
psql -U megacell -d geodjango -f waypoints/create_od_waypoint_view.sql
```

Loading the experiment(s)
==========
To load an experiment into the database, go to `/djange_utils` and open
`orm/load.py`. Set the file path to the appropriate path on your machine, save
and run `django-admin.py shell --settings=settings_geo`
Be sure that you have run all of your migrations, otherwise the following will
take a very long time:
```bash
django-admin.py migrate --settings=settings_geo orm
```
Make sure you have the `outputSmallData.mat` file in the datasets/Phi directory.
This should contain 2 variables: `x_true` and `xLBFGS`, which are loaded into
the database, and associated with the appropriate route. In the shell, execute
```python
from orm import load
load.import_experiment("../data/od_back_map.pickle", "first small experiment")
load.import_experiment_data("first small experiment")
```

Experiment Sensors
==================
From the django shell run
```python
from orm import models
import datetime
e = models.Experiment(description="first small experiment",run_time=datetime.datetime.now())
e.save()
print e.id
from orm import load
# The following assumes you have a route_assignment_matrices_ntt.mat in the data
# folder, as well as a sensors.csv file
load.import_experiment_sensors("first small experiment")
```

Updates
=======
If you ran most of these a while ago, you may have to go back and run all of
Waypoints and the `load.import_lookup()` from Origins.
