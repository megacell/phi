DROP TABLE waypoint_voronoi;
CREATE TABLE waypoint_voronoi (id integer, geom geometry, density_id integer);
CREATE OR REPLACE FUNCTION update_geos() RETURNS integer AS $$
DECLARE
    success integer := 0;
    d integer := 0;
BEGIN
    FOR d IN SELECT density_id FROM orm_waypoint GROUP BY density_id LOOP
        DROP TABLE IF EXISTS waypoint_grouping;
        CREATE TEMPORARY TABLE waypoint_grouping (LIKE orm_waypoint);
        INSERT INTO waypoint_grouping SELECT * FROM orm_waypoint wp WHERE wp.density_id = d;
        INSERT INTO waypoint_voronoi  select id, geom, d from voronoi('waypoint_grouping', 'location') as (id integer, geom geometry);
    END LOOP;
    RETURN success;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM update_geos();

UPDATE orm_waypoint w
SET geom = sq.geom
FROM (
    SELECT v.geom AS geom, w.id AS w_id
    FROM orm_waypoint w, waypoint_voronoi v
    WHERE ST_Contains(v.geom, w.location) AND v.density_id = w.density_id
    ) AS sq
WHERE w_id = w.id;
