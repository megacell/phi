DROP TABLE IF EXISTS waypoint_density CASCADE;
CREATE TABLE waypoint_density (density integer);
INSERT INTO waypoint_density SELECT w.density_id FROM orm_waypoint w GROUP BY w.density_id;

DROP MATERIALIZED VIEW IF EXISTS experiment2_waypoint_od_bins;
CREATE MATERIALIZED VIEW experiment2_waypoint_od_bins AS
SELECT r.od_route_index AS od_route_index,  r.orig_taz AS origin,
array(
  SELECT w.id 
  FROM orm_waypoint w 
  WHERE wd.density = w.density_id and ST_Intersects(w.geom, r.geom)
  ORDER BY w.id
) AS waypoints,
r.dest_taz AS destination,
wd.density as density_id
FROM experiment2_routes r cross join waypoint_density wd;
