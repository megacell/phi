-- Experimented generated from agent trajectories (OD)
DROP TABLE IF EXISTS agent_trajectory_experiment;
CREATE TABLE agent_trajectory_experiment AS
    SELECT R.id, A.orig, A.dest, A.route_choice,
        count(A.route_choice) AS route_split, C.waypoints
    FROM (SELECT B.orig, B.dest, B.m,
        CASE 
            WHEN B.m<=0.2 THEN -1 -- Threshold of 0.2
            WHEN s1=B.m THEN 0
            WHEN s2=B.m THEN 1
            WHEN s3=B.m THEN 1
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
    ORDER BY A.orig, A.dest, A.route_choice;
GRANT ALL ON agent_trajectory_experiment TO megacell;

-- UPDATE table with normalized values, then add to experimentroutes table
ALTER TABLE agent_trajectory_experiment ALTER route_split TYPE float;
UPDATE agent_trajectory_experiment D
SET route_split = C.route_split
FROM (SELECT B.id, B.route_split/A.total as route_split
    FROM (SELECT orig, dest, sum(route_split) as total
        FROM agent_trajectory_experiment
        GROUP BY orig, dest) A,
    agent_trajectory_experiment B
    WHERE A.orig = B.orig AND A.dest = B.dest) C
where D.id = C.id;
