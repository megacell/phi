import unittest

from django_utils.experiments.experiment2.database_setup.route_creator import RouteCreator


class MockTrajectory:
    def __init__(self, d):
        self._d = d
        self.od_taz = (1,1)
    def match_percent(self, other):
        return min(self._d, other._d)


class RouteCreatorTest(unittest.TestCase):
    def test_extract_route(self):
        d = [1,1,.5,.5,.25,.25]
        trajectories = [MockTrajectory(i) for i in d]
        group = RouteCreator(.8)
        group.set_trajectories(trajectories)

        t, matches = group.extract_route()

        self.assertEqual(sorted(trajectories[:2]), sorted(list(matches)))
        self.assertTrue(t in trajectories[:2])

    def test_extract_all_routes(self):
        d = [1,1,.5,.5,.25,.25]
        trajectories = [MockTrajectory(i) for i in d]
        group = RouteCreator(.8)
        group.set_trajectories(trajectories)

        l = group.extract_all_routes()

        self.assertEquals(len(l), 1)

if __name__ == '__main__':
    unittest.main()