import numpy as np
class StatsAggregator:
    def __init__(self, trajectory, matches):
        self.trajectory = trajectory
        self.od_taz_id = trajectory.od_taz
        self._agent_count = len(matches)
        times = [i.travel_time for i in matches]
        if times == None or len(times) == 0 or None in times:
            times = [0]
        try:
            self.average = np.mean(times)
            self.var = np.var(times)
            self.min = np.min(times)
            self.max = np.max(times)
        except:
            self.average = 0
            self.var = 0
            self.min = 0
            self.max = 0
            print times

    def __str__(self):
        return str({"average":self.average, "var":self.var, "min":self.min, "max":self.max})

    def __repr__(self):
        return str(self)

class RouteCreator:
    def __init__(self, similarity_ratio):
        self.similarity_ratio = similarity_ratio
        self.trajectories = set()

    def extract_route(self):
        max_matching_trajectories = []
        prototype_trajectory = None

        for t1 in self.trajectories:
            matches = [t2 for t2 in self.trajectories if (t1.match_percent(t2) > self.similarity_ratio)]

            if len(matches) > len(max_matching_trajectories):
                max_matching_trajectories = matches
                prototype_trajectory = t1

        return prototype_trajectory, max_matching_trajectories

    def set_trajectories(self, trajectories):
        self.trajectories = set(trajectories)

    @staticmethod
    def make_route(t, matches):
        return StatsAggregator(t, matches)

    def extract_all_routes(self):
        l = list()
        trajectory_size = 0
        while len(self.trajectories) != 0 and len(self.trajectories) != trajectory_size:
            trajectory_size = len(self.trajectories)
            t, matches = self.extract_route()
            if (t != None):
                l.append(self.make_route(t, matches))
            self.trajectories.difference_update(matches)

        return l
