Experiment 2 Setup
====================

Parts
-------------------------------
0.	Updating
1.	Clone Repositories
2.	Database
3.	Python
4.	Experiments

Updating
-------------------------------
Before we get started with the installation process, make sure your package manager is up to date.
Run:

    sudo apt-get update
    sudo apt-get upgrade


Cloning Repositories
-------------------------------
To run the traffic experiments, there are two code repositories that need to be cloned.

To start off, you will need to install git if it isn't installed already. Open the terminal and run the command:

    sudo apt-get install git

Make a directory in your home directory. I called mine traffic, but you can name it anything you like.

    cd ~
    mkdir traffic
    cd traffic/

Once you are in this directory, you can clone the two code repositories. Just run:

    git clone https://github.com/megacell/phi
    git clone https://github.com/ion599/optimization.git

As a sanity check, take a look in the two folders created, and see if there are some files and folders created.

Database
-------------------------------
The project uses PostgresSQL as a data store and PostGIS as a spatial library to create the experiment matrices. This section covers the installation process for both of these packages.

### Installing Postgres and Dependencies

We are currently using PostgresSQL version 9.3 for this project. We are using materialized views. This feature was introduced in version 9.3, so any version of Postgres newer than 9.3 should work.

To install PostgresSQL (and some additional tools), run:

    sudo apt-get install postgresql postgresql-contrib pgadmin3 postgresql-server-dev-9.3

For PostGIS:

    sudo apt-get install postgresql-9.3-postgis-2.1

For plpython:

    sudo apt-get install postgresql-plpython

### Configuring the Database

We need to configure the database to use the PostGIS. In this section we create a user and set up a spatial database.

First we are creating a postgis template database. Run:

    sudo -u postgres createdb template_postgis

We need to enable the the procedural language pgSQL. This allows us to run procedural scripts written in a modified SQL language. (This may already be installed)

    sudo -u postgres createlang plpgsql template_postgis

Next, we need to update the template to contain definitions for the spatial data types and functions.

    sudo -u postgres psql template_postgis -f `pg_config --sharedir`/contrib/postgis-2.1/postgis.sql

And add the spatial reference table:

    sudo -u postgres psql template_postgis -f `pg_config --sharedir`/contrib/postgis-2.1/spatial_ref_sys.sql

Finally, we create the a table called geodjango from the template:

    sudo -u postgres createdb -T template_postgis geodjango

We need to create a user, so our application can access the data without going through the administrative account for the db. To do this, run:

    sudo -u postgres psql

Once you are in the postgres console, run:

    CREATE USER megacell;
    ALTER DATABASE geodjango OWNER TO megacell;
    GRANT ALL PRIVILEGES ON DATABASE geodjango TO megacell;

Type `\q` to exit.

To create the `plpythonu` language for the `geodjango` database, first open the database shell:

    psql -U postgres -d geodjango

Then run:

    CREATE LANGUAGE plpythonu;


Here are the old instructions:
> You will need to modify the `pg_hba.conf` file to change the authentication on the megacell user.
>
> We are going to trust local modifications to the db from the megacell user. Open `pg_hba.conf` and add the following line to the file:
>
>     local   geodjango        megacell                                trust
>
> Directly below:
>
>     # Database administrative login by Unix domain socket
>     local   all             postgres                                peer
>
>     # TYPE  DATABASE        USER            ADDRESS                 METHOD

I found it to be easier to grant permissions to all local connections if you
aren't worrying about limiting access to other people sharing the same local
machine. Just comment out all lines starting with `local` and add this line:

    local   all             all                                      trust


Save and then restart postgres:
    sudo service postgresql restart

Python
-------------------------------
Most of the project is written in Python. In this section, we configure and install the Python packages needed for the project.

### Installing Python

If python is not already installed on your machine, run

    sudo apt-get install python

Run `python -V` to confirm you have a 2.7.* version installed.

We will also need the dev tools:

    sudo apt-get install python-dev

### Installing Packages
Install the numerical libaries and accessories:

    sudo apt-get install libblas3gf libblas-dev liblapack3gf liblapack-dev python-numpy python-scipy python-matplotlib ipython

Install the Python package manager(pip) with:

    sudo apt-get install python-pip

Update the setuptools:

    sudo pip install -U setuptools

Install the required packages for the two projects:

    sudo pip install -r ~/traffic/phi/requirements.txt
    sudo pip install -r ~/traffic/optimization/requirements.txt

Experiments
-------------------------------

### Downloading Datasets
You will need to generate an RSA key pair to access the data server. You can take a look on [github](https://help.github.com/articles/generating-ssh-keys) on how to to do this.

Email me (ld283@cornell.edu) or Steven (steve.yadlowsky@berkeley.edu) your public key and we will add it to the server.

run

    rsync -e ssh -rzv ubuntu@ec2-54-212-249-155.us-west-2.compute.amazonaws.com:datasets ~/traffic

### Modifying the config.py Files
You will need to point the configuration file to the correct dataset directory. Without this configured, the code will not know where to look for data files or save any outputs files.

In `~/traffic/phi/django_utils/config.py` you will see something like this:

    ACCEPTED_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'WARN']

    DATA_DIR = '/home/<your user name here>/traffic/datasets/Phi' # FIXME replace with your data path
    EXPERIMENT_MATRICES_DIR = 'experiment_matrices'
    ESTIMATION_INFO_DIR = 'estimation_info'
    WAYPOINTS_FILE = 'waypoints-950.pkl'
    WAYPOINT_DENSITY = 950
    canonical_projection = 4326
    google_projection = 3857 # alternatively 900913
    EPSG32611 = 32611

    NUM_ROUTES_PER_OD = 3
    SIMILARITY_FACTOR = .8
    import os
    # The directory must exist for other parts of this application to function properly
    assert(os.path.isdir(DATA_DIR))

Modify the `<your user name here>` with the name of your home directory.

Similarly, modify `~/traffic/optimization/python.config.py`

### Import Data into the Database

#### Create DB Schema
First, you need to export the `/home/<user>/traffic/phi' and `/home/<user>/traffic/phi/django_utils' paths to the `PYTHONPATH` variable. This lets the python interpreter where to look for packages.

    export PYTHONPATH=$PYTHONPATH:/home/<user>/traffic/phi:/home/<user>/traffic/phi/django_utils

You can modify your .bashrc file to contain this line, so you don't have to run this command everytime you open the terminal.

To install the database schema, run:

    cd ~/traffic/phi/django_utils/
    ./manage.py syncdb --settings=settings_geo
    ./manage.py migrate --settings=settings_geo
(Note: Django 1.7 was released on September 2, 2014. Django now has built in support for schema migrations. I've removed south and updated the project to use the built in migration library.)
#### Populate Data
We populate all the database fields in this step. This is the longest running step in setting up the experiments. Before doing this, make sure you can leave your machine on for **4-10 hours**.

We first need to load sensors and waypoint information. To do this, we need to bring up the django shell:

    cd ~/traffic/phi/django_utils/
    ./manage.py shell

Once the shell is open run:

    from orm import load
    load.import_all()

This will populate the database with the correct sensor and waypoint information.

Now we need to load trajectories, create routes, etc. While still in the shell, run:

    from experiments.experiment2 import run_experiment
    run_experiment.setup_db()

### Running Experiments

To generate the matrices we used for the ISTTT paper, open the django console run:

    from experiments.experiment2 import run_experiment
    run_experiment.generate_experiment_matrices()

This will create all the matrices and save them in the experiment_matrices directory.

To calculate the results, change directories into the optimization project and run:
    python main.py --solver=BB --log==DEBUG

### Making Plots
To generate the plots in the submitted ISTTT paper, change directories into the `optimization/python` directory and run:
    python plot_error_vs_route_usage.py
    python waypoint_plots.py

### Running the visualization server
Go to the visualizations folder:

    cd ~/traffic/phi/visualization

First install the dependencies:

    pip install -r requirements.txt

First sync and migradethe databases:

    ./manage.py syncdb
    ./manage.py migrate

Then run the shell

    ./manage.py shell

For testing, import the dummy data:

    run phidata/data_import/dummy_data.py

Otherwise, import cell, link and route data:

    run phidata/data_import/cell_data.py
    run phidata/data_import/link_data.py
    run phidata/data_import/route_data.py

To deploy a public server, follow the instructions
[here][https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/modwsgi/]


### Architecture of Experiment 2

The experiments uses data from datasets that are set in `config.py`. The
following steps are run in `setup_db` from
`experiments/experiment2/run_experiment.py` to load the data:

* `create_experiment2`: sets up metaparameters (ignore unless it breaks, should be removed)
* Link loader (`lgl.load_LA_links()`):
    - A link is a line segment representing part of a road
    - **Input:** Takes in shape files from `LINKS_FILES` directory as specified in the
      config, reads it and loads the links.
    - **Tables changed:** Creates `link_geometry` table in the database
    - Stores different projections of the coordinates of each link in the
      database table (eg. canonical projection: eggs4326 projection, wgs84)
    - Optimized loading using `stringIO`
* Trajectory loader (`tl.load()`):
    - **Input:** Loads trajectories from a `.csv` file into the database
    - **Tables changed:** `experiment2_trajectories` created
    - Each trajectory is stored as a sequence of links along with other metadata:
        + `agent_id` : person driving
        + `commute_direction`: morning or evening
        + `orig_TAZ`, `dest_TAZ`: origin and destination
        + `link_ids`: ids of each link in the sequence of links traversed
    - Notes:
        + `CREATE INDEX` doesn't make a difference
        + `orig_TAZ`, `dest_TAZ` should be integers but are floats
* Route loader (`rl.load()`)
    - **Input:** Existing link and trajectory data
    - **Tables changed:** `experiment2_routes` created
    - A route is a bundle of similar trajectories (Similarity is determined by
      `config.SIMILARITY_FACTOR` in `route_creater.py`)
    - Caching of the links is first done in `import_link_geometry_table`, which
      is important for speed
    - First group trajectories by od-pairs (`RouteLoader.import_trajectory_groups`)
    - In `route_creater.py`, group trajectories from each od pair that are
      similar enough into one route (Happens in `Trajectory.match_percent` in
      `RouteCreater`), which is represented by the origin and destination TAZs,
      links in the route, as well as the number of agents taking the route.
* Waypoint loader (`lw.import_waypoints()`)
    - **Input:** Waypoints files containing coordinates of waypoints (Either
      synthetically generated or real cell-tower locations)
    - **Tables changed:** `orm_waypoint`, schemea defined in `orm.models.Waypoint`
    - Waypoints are the cell-tower locations, `density_id` is used everywhere to
      uniquely identify each set of waypoints. To add a new set of waypoints, we
      need to provide a unique `density_id`
    - This happens in `orm.load.import_waypoints`
    - Notes:
        + Removing autocommit and manually committing wasn't needed
* Waypoint sequences (The `.sql` files run in `setup_db`)
    - **Input:** Waypoints data loaded from before
    - **Tables changed:** Creates `waypoint_voronoi`, which is a table
      containing the voronoi partitions for each waypoint, and updates
      `orm_waypoint` with the computed partitions. Also creates tables
      `waypoint_density` and `experiment2_waypoint_od_bins`
    - `voronoi_python.sql`: loads voronoi_partition function (verbatim)
    - `set_waypoint_voronoi.sql`: for each waypoint density,
    - `waypoint_sequences.sql`: calculates how the route intersects sequences of
       waypoints (slowest part of importing the data) generates a table of links
       and intersecting waypoints. Builds a waypoint sequence for each
       route. (take a look at for bugs)
    - `create_od_waypoint_view.sql`: Creates more waypoint tables
* Phi (`get_phi()` in `run_experiment.py`):
    - **Input:** `experiment2_routes` table
    - **Output:** `phi.pkl` in the data directory, which is a route-sensor
      mapping, regenerate when routes used changes.
* Generating experiment matrices (`run_experiment.matrix_generator`)
    - There's three different lines in `matrix_generator`:
        + `return waypoints.WaypointMatrixGenerator(phi,routes,waypoint_density)`: Experiment matrices (ignores OD-flows)
        + `return separated.WaypointMatrixGenerator(phi,routes,waypoint_density)`: Control matrices
        + `return waypoints_od.WaypointODMatrixGenerator(phi,routes,waypoint_density)`: Never use this, more information than we ever knows
