import unittest

from django.contrib.gis.geos import LineString

from django_utils.experiments.experiment2.trajectory_processing.trajectory import Trajectory


class TestTrajectory(unittest.TestCase):
    def setUp(self):
        # create some lines
        id_to_geometry = dict()
        id_to_geometry[0] = LineString([(0,0),(0,1)])
        id_to_geometry[1] = LineString([(0,1),(0,2)])
        id_to_geometry[2] = LineString([(0,2),(0,3)])
        id_to_geometry[3] = LineString([(0,3),(0,4),(4,7)])

        self.id_to_geometry = id_to_geometry

    def test_length(self):
        t = Trajectory([1,2], None, self.id_to_geometry)
        self.assertAlmostEqual(t.length(), 2, delta=.0001)

    def test_length_complex(self):
        t = Trajectory([3], None, self.id_to_geometry)
        self.assertAlmostEqual(t.length(), 6, delta=.0001)

    def test_match_percent(self):
        t1 = Trajectory([0,1], None, self.id_to_geometry)
        t2 = Trajectory([0], None, self.id_to_geometry)
        self.assertAlmostEqual(t1.match_percent(t2), 0.5, delta=.0001)

    def test_match_percent_no_overlapping_segments(self):
        t1 = Trajectory([0], None, self.id_to_geometry)
        t2 = Trajectory([1], None, self.id_to_geometry)
        self.assertAlmostEqual(t1.match_percent(t2), 0, delta=.0001)

    def test_match_percent_all_overlapping_segments(self):
        t1 = Trajectory([0], None, self.id_to_geometry)
        t2 = Trajectory([0], None, self.id_to_geometry)
        self.assertAlmostEqual(t1.match_percent(t2), 1, delta=.0001)

if __name__ == '__main__':
    unittest.main()