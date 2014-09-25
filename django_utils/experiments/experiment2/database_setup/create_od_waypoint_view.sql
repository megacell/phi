DROP TABLE IF EXISTS waypoint_density CASCADE;
CREATE TABLE waypoint_density (density integer);
INSERT INTO waypoint_density SELECT w.density_id FROM orm_waypoint w GROUP BY w.density_id limit 2;

DROP MATERIALIZED VIEW IF EXISTS experiment2_waypoint_od_bins;
DROP TABLE IF EXISTS experiment2_waypoint_od_bins;

CREATE TABLE experiment2_waypoint_od_bins AS
SELECT r.od_route_index AS od_route_index, r.orig_taz AS origin,
array(
  SELECT w.id 
  FROM orm_waypoint w 
  WHERE wd.density = w.density_id and ST_Intersects(w.geom, r.geom)
  ORDER BY w.id
) AS waypoints,
r.dest_taz AS destination,
wd.density as density_id,
r.geom as geom
FROM experiment2_routes r cross join waypoint_density wd;

CREATE OR REPLACE FUNCTION get_waypoint_sequence(trajectory geometry, waypoints integer[]) RETURNS integer[] AS $$
DECLARE
    n integer := 0;
    result integer[] := ARRAY[]::integer[];
    line geometry;
BEGIN
    FOR n IN 1.. ST_NumGeometries(trajectory)  LOOP
        line = ST_GeometryN(trajectory, n);
        result = result || (
            SELECT array_agg(ow.id)
            FROM UNNEST(waypoints) w
            INNER JOIN orm_waypoint ow
            ON ow.id = w
            WHERE ST_Intersects(line, ow.geom)
            );
    END LOOP;
    RETURN result;
END $$ LANGUAGE plpgsql;
/*
WITH duplicate_bins AS
(
    SELECT
    bins.waypoints as waypoints,
    bins.od_route_index as od_route_index,
    bins.origin as origin,
    bins.destination as destination,
    bins.geom,
    bins.density_id
    FROM experiment2_waypoint_od_bins bins
	INNER JOIN
	(
	    SELECT waypoints, density_id
		FROM (
			SELECT
			waypoints AS waypoints,
			density_id as density_id,
			COUNT(waypoints) AS waypointcount
			FROM experiment2_waypoint_od_bins
			GROUP BY waypoints, density_id) s
		WHERE s.waypointcount>1
	) w
	ON bins.waypoints = w.waypoints and bins.density_id = w.density_id
)

UPDATE experiment2_waypoint_od_bins original_bins
SET waypoints=get_waypoint_sequence(b.geom, b.waypoints)
FROM duplicate_bins b
WHERE original_bins.origin = b.origin
AND original_bins.destination = b.destination
AND original_bins.od_route_index = b.od_route_index
AND original_bins.density_id = b.density_id;
*/