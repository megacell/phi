__author__ = 'lei'
from imposm.parser import OSMParser
import pickle
import cStringIO as sio
from collections import defaultdict
# simple class that handles the parsed OSM data.
class HighwayCounter(object):

    def __init__(self):
        self.highways = 0
        self.tags = set()
        self.highwaylist = []
    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'highway' in tags:
                self.tags.add(tags['highway'])
                print refs
                self.highways += 1
                self.highwaylist.append((osmid, tags['highway']))
                #print self.tags

def coords_callback(coords):
    for osm_id, lon, lat in coords:
        if (osm_id%1000000) == 0:
            print '%s %.4f %.4f' % (osm_id, lon, lat)
# instantiate counter and parser and start parsing
counter = HighwayCounter()
#p = OSMParser(concurrency=None, ways_callback=counter.ways, coords_callback=coords_callback)
#p.parse('/home/lei/traffic/datasets/Phi/california-latest.osm.pbf')

# done
#print counter.highways
#print counter.tags
#print counter.highwaylist

#pickle.dump(counter.highwaylist,open('highwaylist.pkl','w'))
def load_db():
    from django.db import connection
    highwaylist = pickle.load(open('highwaylist.pkl'))
    rows = sio.StringIO()
    for i in highwaylist:
        rows.write(str(i[0]) + "\t"+'"' + i[1]+'"' + '\n')
    rows.reset()
    cursor = connection.cursor()

    sql_query = '''
    DROP TABLE IF EXISTS link_type;
    CREATE TABLE link_type (link_id int, type varchar);'''

    cursor.execute(sql_query)

    cursor.copy_from(rows, 'link_type')

def count_trajectories(typelist):
    from django.db import connection

    cursor = connection.cursor()
    sql_query = '''
    select distinct type from link_id_type;
    '''
    cursor.execute(sql_query)
    types = [i for i, in cursor]

    sql_query = '''
        select link_id, type from link_id_type;
        '''
    cursor.execute(sql_query)

    typemap = {k:v for k,v in cursor}

    counter = defaultdict(lambda : 0)

    sql_query = '''
    select link_ids from experiment2_trajectories;
    '''
    types = set(typelist)
    count = 0
    cursor.execute(sql_query)
    for links, in cursor:
        remapped_links = set()
        remapped_links.update(typemap[i] for i in links)
        if len(types.intersection(remapped_links)) != 0:
            count+=1

    return count

def plot_link_counts():
    from django.db import connection
    sql_query = '''select lit.type, count(*) from link_id_type lit group by lit.type;'''
    cursor = connection.cursor()
    cursor.execute(sql_query)
    types = []
    counts = []
    for t, c in cursor:
        types.append(t)
        counts.append(c)

    import numpy as np
    import matplotlib.pyplot as plt

    N = len(counts)
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    plt.bar(ind, counts, width)

    plt.ylabel('Link Count')
    plt.title('Count of Links')
    plt.xticks(ind+width/2., types )
    print types
    print counts
    plt.show()

def plot_cumulative_type_usage():
    types = [u'"motorway"',
     u'"motorway_link"',
     u'"primary"',
     u'"primary_link"',
     u'"trunk"',
     u'"trunk_link"',
     u'"secondary"',
     u'"unclassified"',
     u'"tertiary"',
     u'"living_street"']
    graphtypes = []
    ct = []
    for t in types:
        graphtypes.append(t)
        ct.append(count_trajectories(graphtypes))
        print ct
    import numpy as np
    import matplotlib.pyplot as plt

    N = len(ct)
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    plt.bar(ind, ct, width)

    plt.ylabel('Trajectory Count')
    plt.title('Cumulative Trajectory Usage')

    plt.xticks(ind+width/2., [i.strip('"') for i in types])
    plt.show()

plot_link_counts()
#plot_cumulative_type_usage()