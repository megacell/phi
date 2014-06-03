DROP TABLE waypoint_od_bins;
CREATE MATERIALIZED VIEW waypoint_od_bins AS SELECT r.id AS orm_route_id, (SELECT w.id FROM orm_waypoint w WHERE ST_Contains(w.geom, ST_StartPoint(r.geom))) AS origin,array(SELECT w.id from orm_waypoint w WHERE ST_Intersects(w.geom, r.geom)) AS waypoints, (SELECT w.id FROM orm_waypoint w WHERE ST_Contains(w.geom, ST_EndPoint(r.geom))) AS destination FROM orm_route r;
