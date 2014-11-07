Loading Waypoints
=================
<a href="waypoints"></a>
```bash
export PYTHONPATH=$PYTHONPATH:<REPOSITORY_HOME>:<REPOSITORY_HOME>/django_utils
```
Given a waypoint pickle file `waypoints-???.pkl` in the data folder:

1. Clear the waypoints table in the database via `psql -U megacell -d geodjango`:
```sql
DELETE from orm_waypoint;
```

1. `django-admin.py shell --settings=settings_geo`

2. In the shell,
```python
from orm import load
load.import_waypoints()
```
3. Exit shell.
4. `psql -U megacell -d geodjango -f set_waypoint_voronoi.sql`
5. `psql -U megacell -d geodjango -f create_od_waypoint_view.sql` (takes a while)

Now, you have access to the `waypoint_od_bins` 
view. It is a materialized view so that it doesn't have to perform that
expensive query every time. If you make any changes to the waypoints, routes,
or origins, you can refresh the view via: `psql -U megacell -d geodjango`
```sql
REFRESH MATERIALIZED VIEW waypoint_od_bins;
```

Generating matrices for Experiments 1-3
=======================================
Experiment 1
------------
1. If waypoints have changed, refresh the waypoints in the database. See
[instructions](#waypoints).

Current waypoints file: `waypoints-950.pkl` (update this as needed).

1. Obtain the experiment ID that you are interested in from the database
```postgres
select * from orm_experiment;
```
1. From the regular shell, import the pre-processed MATSim trajectories and run
queries to bucket the route flows by waypoints and by ODs (CAUTION: these files
are in the phi-estimation repo):
```bash
psql -d geodjango -U <SUPERUSER> -f experiments/import_agent_trajectories.sql
psql -d geodjango -U <SUPERUSER> -f experiments/import_agent_experiment.sql
```
1. Extract the matrices from the database.
From the `<REPO_HOME>/django_utils`:
```bash
./manage.py shell
```
From the django IPython shell:
```python
import generate_phi
phi = generate_phi.phi_generation_sql(<EXPERIMENT ID>)
run -i experiments/experiment1.py
run -i experiments/experiment1_control.py
```
1. We run the experiment via the traffic-estimation repo. From an IPython shell
in the python directory (the parent directory):
```python
run -i main.py --log=DEBUG --file=experiment1_control_matrices.mat --solver BB
run -i main.py --log=DEBUG --file=experiment1_matrices.mat --solver BB
```

Experiment 2
------------
(Add documentation as needed)

Experiment 3
------------
(Add documentation as needed)

