-- Experiment generated from agent trajectories (OD)
DROP TABLE IF EXISTS agent_trajectory_experiment;
CREATE TABLE agent_trajectory_experiment (
    id integer DEFAULT -1,
    orig integer,
    dest integer,
    route_choice integer,
    route_value float DEFAULT 0,
    route_split_wp float DEFAULT 0,
    route_split_od float DEFAULT 0,
    waypoints integer[] DEFAULT ARRAY[]::integer[]
);
GRANT ALL ON agent_trajectory_experiment TO megacell;
-- Insert rows for all routes that have some OD flow
INSERT INTO agent_trajectory_experiment (id, orig, dest, route_choice, waypoints)
    SELECT R.id, A.orig_taz as orig, A.dest_taz as dest, 0, C.waypoints
    FROM agent_trajectories A, orm_route as R, waypoint_od_bins as C
    WHERE commute_direction = 0
        AND A.s1 != -1
        AND (A.s1 > 0.2 OR A.s2 > 0.2 OR A.s3 > 0.2)
        AND R.origin_taz = A.orig_taz
        AND R.destination_taz = A.dest_taz
        AND R.od_route_index = 0
        AND C.orm_route_id = R.id
    GROUP BY A.orig_taz, A.dest_taz, R.id, C.waypoints;

INSERT INTO agent_trajectory_experiment (id, orig, dest, route_choice, waypoints)
    SELECT R.id, A.orig_taz as orig, A.dest_taz as dest, 1, C.waypoints
    FROM agent_trajectories A, orm_route as R, waypoint_od_bins as C
    WHERE commute_direction = 0
        AND A.s2 != -1
        AND (A.s1 > 0.2 OR A.s2 > 0.2 OR A.s3 > 0.2)
        AND R.origin_taz = A.orig_taz
        AND R.destination_taz = A.dest_taz
        AND R.od_route_index = 1
        AND C.orm_route_id = R.id
    GROUP BY A.orig_taz, A.dest_taz, R.id, C.waypoints;

INSERT INTO agent_trajectory_experiment (id, orig, dest, route_choice, waypoints)
    SELECT R.id, A.orig_taz as orig, A.dest_taz as dest, 2, C.waypoints
    FROM agent_trajectories A, orm_route as R, waypoint_od_bins as C
    WHERE commute_direction = 0
        AND A.s3 != -1
        AND (A.s1 > 0.2 OR A.s2 > 0.2 OR A.s3 > 0.2)
        AND R.origin_taz = A.orig_taz
        AND R.destination_taz = A.dest_taz
        AND R.od_route_index = 2
        AND C.orm_route_id = R.id
    GROUP BY A.orig_taz, A.dest_taz, R.id, C.waypoints;

-- Fill in the route flow for each route
UPDATE agent_trajectory_experiment D
SET route_value = E.route_value
FROM (SELECT R.id, A.orig, A.dest, A.route_choice,
        count(A.route_choice) AS route_value
    FROM (SELECT B.orig, B.dest, B.m,
        CASE 
            WHEN B.m<=0.2 THEN -1 -- Threshold of 0.2
            WHEN s1=B.m THEN 0
            WHEN s2=B.m THEN 1
            WHEN s3=B.m THEN 2
            ELSE -1
        END
        AS route_choice
        FROM (SELECT orig_TAZ as orig, dest_TAZ as dest,s1,s2,s3,
            GREATEST(s1,s2,s3) as m
            FROM agent_trajectories
            WHERE commute_direction = 0) B
        ) A, orm_route as R, waypoint_od_bins as C
    WHERE R.origin_taz = A.orig
        AND R.destination_taz = A.dest
        AND R.od_route_index = A.route_choice
        AND C.orm_route_id = R.id
    GROUP BY A.orig, A.dest, A.route_choice, R.id, C.waypoints
    ORDER BY A.orig, A.dest, A.route_choice) E
WHERE D.orig = E.orig
    AND D.dest = E.dest
    AND D.route_choice = E.route_choice;

-- UPDATE table with normalized values (by waypoints)
UPDATE agent_trajectory_experiment D
SET route_split_wp = C.route_split_wp
FROM (SELECT B.id, B.route_value/A.total as route_split_wp
    FROM (SELECT orig, dest, waypoints, sum(route_value) as total
        FROM agent_trajectory_experiment
        GROUP BY waypoints, orig, dest) A,
    agent_trajectory_experiment B
    WHERE A.orig = B.orig AND A.dest = B.dest AND A.waypoints = B.waypoints AND A.total != 0) C
where D.id = C.id;

-- UPDATE table with normalized values (by OD)
UPDATE agent_trajectory_experiment D
SET route_split_od = C.route_split_od
FROM (SELECT B.id, B.route_value/A.total as route_split_od
    FROM (SELECT orig, dest, sum(route_value) as total
        FROM agent_trajectory_experiment
        GROUP BY orig, dest) A,
    agent_trajectory_experiment B
    WHERE A.orig = B.orig AND A.dest = B.dest) C
where D.id = C.id;

-- TODO add to experimentroutes table

-- Original query
-- CREATE TABLE agent_trajectory_experiment AS
--     SELECT A.m as max, R.id, A.orig, A.dest, A.route_choice,
--         count(A.route_choice) AS route_value, 1 as route_split_wp,
--         1 as route_split_od --, C.waypoints
--     FROM (SELECT B.orig, B.dest, B.m,
--         CASE 
--             WHEN B.m<=0.2 THEN -1 -- Threshold of 0.2
--             WHEN s1=B.m THEN 0
--             WHEN s2=B.m THEN 1
--             WHEN s3=B.m THEN 2
--             ELSE -1
--         END
--         AS route_choice
--         FROM (SELECT orig_TAZ as orig, dest_TAZ as dest,s1,s2,s3,
--             GREATEST(s1,s2,s3) as m
--             FROM agent_trajectories
--             WHERE commute_direction = 0) B
--         ) A, orm_route as R, waypoint_od_bins as C
--     WHERE R.origin_taz = A.orig
--         AND R.destination_taz = A.dest
--         AND R.od_route_index = A.route_choice
--         AND C.orm_route_id = R.id
--     GROUP BY A.orig, A.dest, A.route_choice, R.id, C.waypoints, A.m
--     ORDER BY A.orig, A.dest, A.route_choice LIMIT 10;
