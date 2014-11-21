DROP TABLE IF EXISTS waypoint_density CASCADE;
CREATE TABLE waypoint_density (density integer);
INSERT INTO waypoint_density SELECT w.density_id FROM orm_waypoint w GROUP BY w.density_id;

DROP MATERIALIZED VIEW IF EXISTS experiment2_waypoint_od_bins;
DROP TABLE IF EXISTS experiment2_waypoint_od_bins;

CREATE TABLE experiment2_waypoint_od_bins AS
SELECT r.od_route_index AS od_route_index, r.orig_taz AS origin,
waypoint_sequence(r.links, wd.density) AS waypoints,
r.dest_taz AS destination,
wd.density as density_id --,
--r.geom as geom
FROM experiment2_routes r cross join waypoint_density wd;