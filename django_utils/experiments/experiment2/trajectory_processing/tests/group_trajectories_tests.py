import unittest

from django_utils.experiments.experiment2.trajectory_processing.group_trajectories import OD_group


class MockTrajectory:
    def __init__(self, d):
        self._d = d
    def match_percent(self, other):
        return min(self._d, other._d)


class TestODGroup(unittest.TestCase):

    def test_largest_set_of_matching_trajectories(self):
        d = [1,1,.5,.5,.25,.25]
        trajectories = [MockTrajectory(i) for i in d]
        group = OD_group(trajectories)
        t, matches = group.largest_set_of_matching_trajectories()
        self.assertEqual(trajectories[:2], list(matches))
        self.assertEqual(trajectories[0], t)

    # performance test
    #def test_large_random_distance_matrix(self):
    #    import random
    #    t = [MockTrajectory(random.random()) for i in range(10000)]
    #    group = OD_group(t)
    #    group.largest_set_of_matching_trajectories()

if __name__ == '__main__':
    unittest.main()