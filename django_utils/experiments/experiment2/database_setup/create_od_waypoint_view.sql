DROP MATERIALIZED VIEW IF EXISTS experiment2_waypoint_od_bins;

CREATE MATERIALIZED VIEW experiment2_waypoint_od_bins AS
SELECT r.od_route_index AS od_route_index,  r.origin_taz AS origin,
array(
  SELECT w.id 
  FROM orm_waypoint w 
  WHERE ST_Intersects(w.geom, r.geom) 
  ORDER BY w.id
) AS waypoints,
r.destination_taz AS destination
FROM orm_experiment2route r;
