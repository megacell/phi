from mpl_toolkits.basemap import Basemap, shiftgrid, cm
import numpy as np
import matplotlib.pyplot as plt
from django.contrib.gis.geos.linestring import LineString, GEOSGeometry


def get_links():
    from django.db import connection
    sql_query = "SELECT link_id, geom FROM link_geometry;"
    cursor = connection.cursor()
    cursor.execute(sql_query)
    return {id:geom for id, geom in cursor}

def get_link_type_map():
    from django.db import connection
    sql_query ='''select link_id, type from link_id_type;'''
    cursor = connection.cursor()
    cursor.execute(sql_query)
    return {id:type for id, type in cursor}

def get_link_types():
    from django.db import connection
    sql_query ='''select distinct type from link_id_type;'''
    cursor = connection.cursor()
    cursor.execute(sql_query)
    return [i for i, in cursor]

def plotline(m, line, color):
    xs, ys = zip(*line.coords)
    xs, ys = m(xs, ys)
    m.plot(xs, ys, color=color)
def plotroadtype(type, fig):
    ax = fig.add_axes([0.1,0.1,0.8,0.8])
    # setup of basemap ('lcc' = lambert conformal conic).
    # use major and minor sphere radii from WGS84 ellipsoid.

    m = Basemap(llcrnrlon=-118.383626300001,llcrnrlat=33.9309546999998,urcrnrlon=-117.6511386,urcrnrlat=34.2734052999999,\
                ellps='WGS84',\
                resolution='i',area_thresh=1.,projection='merc',\
                ax=ax)

    links = get_links()
    linktypes = get_link_type_map()
    for id in links.keys():
        if linktypes[id] != type:
            continue
        plotline(m, GEOSGeometry(links[id]), 'b')
linktypes = get_link_types()
linktypes = [u'"motorway"', u'"motorway_link"', u'"primary"', u'"primary_link"', u'"trunk"', u'"trunk_link"', u'"secondary"']
fig = plt.figure()
for i, linktype in zip(range(len(linktypes)),linktypes):
    print linktype
    plotroadtype(linktype, fig)
    title = "plots/" + str(i) + ": " + linktype.strip('"')
    plt.title(title)
    plt.savefig(title, format='svg')

