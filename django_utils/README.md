Loading Waypoints
=================
Given a waypoint pickle file `waypoints.pkl` in the data folder:
1. `django-admin.py shell --settings=settings_geo`
2. In the shell,
```python
from orm import load
load.import_waypoints()
```
3. Exit shell.
4. `psql -U megacell -d geodjango -f set_waypoint_voronoi.sql`
5. `psql -U megacell -d geodjango -f create_od_waypoint_view.sql`

Now, you have access to the `waypoint_od_bins` view. It is a materialized view
so that it doesn't have to perform that expensive query every time. If you make
any changes to the waypoints, routes, or origins, you can refresh the view via:
`psql -U megacell -d geodjango`
```sql
REFRESH MATERIALIZED VIEW waypoint_od_bins
```
