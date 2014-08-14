from django.contrib.gis.geos import LineString, MultiLineString, Point
class Trajectory:
    def __init__(self, id_sequence, od_taz, geometry_map):
        self._id_sequence = id_sequence
        self.od_taz = od_taz
        self._length = -1
        self._geometry_map = geometry_map
        self._start_point = self.get_start_point()
        self._end_point = self.get_end_point()

    def _trajectory_length(self, sequence):
        length = 0
        for i in sequence:
            length += self._geometry_map[i].length
        return length

    def length(self):
        if self._length < 0:
            self._length = self._trajectory_length(self._id_sequence)
        return self._length

    def match_percent(self, other):
        a = set(self._id_sequence)
        b = set(other._id_sequence)
        c = a.intersection(b)
        return self._trajectory_length(c) / max(self.length(), other.length())

    def convert_to_LineString(self, multiline=False):
        multiline = None
        for id in self._id_sequence:
            if (multiline == None):
                g = self._geometry_map[id]
                multiline = MultiLineString(g)
                multiline.set_srid(g.get_srid())
            else:
                multiline.append(self._geometry_map[id])
        return multiline.merged

    def get_start_point(self):
        g = self._geometry_map[self._id_sequence[0]]
        p = Point(g[0])
        p.set_srid(g.get_srid())
        return p

    def get_end_point(self):
        g = self._geometry_map[self._id_sequence[-1]]
        p = Point(g[-1])
        p.set_srid(g.get_srid())
        return p
    def __repr__(self):
        return str(self.od_taz)