import unittest

from django_utils.experiments.experiment2.database_setup.route_creator import RouteCreator


class MockTrajectory:
    def __init__(self, d):
        self._d = d
    def match_percent(self, other):
        return min(self._d, other._d)


class RouteCreatorTest(unittest.TestCase):
    def test_extract_route(self):
        d = [1,1,.5,.5,.25,.25]
        trajectories = [MockTrajectory(i) for i in d]
        group = RouteCreator(.8, trajectories)
        t, matches = group.extract_route()
        self.assertEqual(trajectories[:2], list(matches))
        self.assertEqual(trajectories[0], t)

    def test_extract_all_routes(self):
        d = [1,1,.5,.5,.25,.25]
        trajectories = [MockTrajectory(i) for i in d]
        group = RouteCreator(.8, trajectories)

        l = group.extract_all_routes()

        self.assertEquals(len(l), 1)

if __name__ == '__main__':
    unittest.main()