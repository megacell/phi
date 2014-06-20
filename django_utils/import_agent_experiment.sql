DROP TABLE IF EXISTS agent_trajectory_experiment;
CREATE TABLE agent_trajectory_experiment AS
    SELECT R.id, A.orig, A.dest, A.route_choice,
        count(A.route_choice) AS value 
    FROM (SELECT B.orig, B.dest, B.m,
        CASE 
            WHEN B.m<=0.2 THEN -1
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
        ) A, orm_route as R
    WHERE R.origin_taz = A.orig
        AND R.destination_taz = A.dest
        AND R.od_route_index = A.route_choice
    GROUP BY A.orig, A.dest, A.route_choice, R.id
    ORDER BY A.orig, A.dest, A.route_choice;
GRANT ALL ON agent_trajectory_experiment TO megacell;

