from collections import defaultdict
import itertools
MATCH_PERCENTAGE = 0.8

def group_by_od(trajectories):
    #print trajectories[:10]
    d = defaultdict(list)
    for trajectory in trajectories:
        d[trajectory.od_taz].append(trajectory)

    return { k:OD_group(d[k]) for k in d.keys()}


class OD_group:
    def __init__(self, trajectories):
        self._trajectories = set(trajectories)
        assert(len(trajectories) == len(self._trajectories))

    def largest_set_of_matching_trajectories(self):
        max_matching_trajectories = []
        prototype_trajectory = None
        for t1 in self._trajectories:
            matches = []
            for t2 in self._trajectories:
                if (t1.match_percent(t2) > MATCH_PERCENTAGE):
                    matches.append(t2)
            if len(matches) > len(max_matching_trajectories):
                max_matching_trajectories = matches
                prototype_trajectory = t1
        return prototype_trajectory, max_matching_trajectories

    def get_matches(self, n):
        l = list()
        startsize = len(self._trajectories)
        for i in range(n):
            t, matches = self.largest_set_of_matching_trajectories()
            l.append(( t, matches))
            self._trajectories.difference_update(matches)
            #print('trajectories remaining:' + str(len(self._trajectories)))
            if len(self._trajectories) == 0:
                #print('exiting trajectory')
                break

        if not (startsize >= len(l)):
            print self._trajectories
            print l
        assert (startsize >= len(l))
        return l

