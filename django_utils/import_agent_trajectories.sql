DROP TABLE IF EXISTS agent_trajectories;
CREATE TABLE agent_trajectories (
  agent_id integer,
  commute_direction integer,
  orig_n integer,
  dest_n integer,
  orig_TAZ float,
  dest_TAZ float,
  s1 float,
  s2 float,
  s3 float
);
\copy agent_trajectories FROM '../data/agents_500k.csv' WITH CSV HEADER;
GRANT ALL ON agent_trajectories TO megacell;
