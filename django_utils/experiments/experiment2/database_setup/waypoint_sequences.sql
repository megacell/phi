DROP FUNCTION waypoint_sequence(integer[], integer);

CREATE OR REPLACE FUNCTION clear_sequence_dictionary() RETURNS integer AS $$
if 'linkmap' in SD:
    del SD['linkmap']
return 1
$$ LANGUAGE plpythonu;

select * from clear_sequence_dictionary();

CREATE OR REPLACE FUNCTION waypoint_sequence(link_list integer[], density integer) RETURNS integer[] AS $$
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
        sql = '''
        select g.link_id as l, w.density_id as d, array_agg(w.id) as wp
        from link_geometry g
        inner join orm_waypoint w
        on ST_Intersects(g.geom, w.geom)
        group by g.link_id, w.density_id;
        '''
        result = plpy.execute(sql)
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
                plpy.warning('not found' + str((l, density)))
            else:
                seq.extend(self.link_map[(l, density)])

        return seq.get_list()

def get_sequence(links, density):
    if not ('linkmap' in SD):
        SD['linkmap'] = LinkMapFactory.get_link_map()
    linkmap = SD['linkmap']
    return SequenceFromSetGenerator(linkmap).get_sequence(links, density)

return get_sequence(link_list, density)
$$ LANGUAGE plpythonu
