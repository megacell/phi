from django.db import connection

class SequenceList:
    def __init__(self):
        self.l = []

    def add(self, v):
        if (len(self.l) == 0 or v != self.l[-1]):
            self.l.append(v)

    def extend(self, vs):
        for v in vs:
            self.add(v)

    def get_list(self):
        return self.l

class LinkMapFactory:
    @staticmethod
    def get_link_map():
        cursor = connection.cursor()
        sql = '''
        select g.link_id as l, w.density_id as d, array_agg(w.id) as wp
        from link_geometry g
        inner join orm_waypoint w
        on ST_Intersects(g.geom, w.geom)
        group by g.link_id, w.density_id;
        '''
        result = cursor.execute(sql)
        mp = dict()
        for row in result:
            mp[(row['l'],row['d'])] = row['wp']
        return mp

class SequenceFromSetGenerator:
    def __init__(self, link_map):
        self.link_map = link_map

    def get_sequence(self, links, density):
        seq = SequenceList()

        for l in links:
            if (l, density) not in self.link_map:
                print ('not found' + str((l, density)))
            else:
                seq.extend(self.link_map[(l, density)])

        return seq.get_list()

'''
UPDATE filtered_waypoint_od_bins b
SET waypoints=waypoint_sequence(r.links, b.density_id)
FROM filtered_routes r
INNER JOIN filtered_waypoint_od_bins bins
ON bins.origin = r.orig_taz
AND bins.destination = r.dest_taz
AND bins.od_route_index = r.od_route_index;
'''
seq_generator = SequenceFromSetGenerator(LinkMapFactory.get_link_map())

sql_query = '''
select r.links, r.orig_taz, r.dest_taz, r.od_route_index
from filtered_routes r
'''
cursor = connection.cursor()
links = [(links, o, d ,index) for links, o, d, index in cursor.execute(sql_query)]