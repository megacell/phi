DROP TABLE waypoint_voronoi;
CREATE TABLE waypoint_voronoi AS SELECT * FROM voronoi('orm_waypoint', 'location') AS (id integer, geom geometry);
UPDATE orm_waypoint w SET geom = sq.geom FROM (SELECT v.geom AS geom, w.id AS w_id FROM orm_waypoint w, waypoint_voronoi v WHERE ST_Contains(v.geom, w.location)) AS sq WHERE w_id = w.id;
