DROP MATERIALIZED VIEW waypoint_od_bins;
CREATE MATERIALIZED VIEW waypoint_od_bins AS
SELECT r.id AS orm_route_id, (
  SELECT matrix_id FROM orm_origin w INNER JOIN orm_matrixtaz ON orm_matrixtaz.taz_id = w.taz_id WHERE ST_Contains(w.geom, ST_StartPoint(r.geom)) LIMIT 1
) AS origin, array(SELECT w.id from orm_waypoint w WHERE ST_Intersects(w.geom, r.geom)) AS waypoints, (
  SELECT matrix_id FROM orm_origin w INNER JOIN orm_matrixtaz ON orm_matrixtaz.taz_id = w.taz_id WHERE ST_Contains(w.geom, ST_EndPoint(r.geom)) LIMIT 1
) AS destination
FROM orm_route r;
GRANT ALL ON waypoint_od_bins TO megacell;
