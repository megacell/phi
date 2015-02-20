from django.db import connection
from django_utils.experiments.experiment2.database_setup.route_loader import RouteLoader
from django_utils.experiments.experiment2.database_setup.route_creator import RouteCreator
import django_utils.config as config
import run_experiment
from django.contrib.gis.geos import Polygon, GEOSGeometry

def get_link_type_map():
    sql_query = '''select link_id, type from link_id_type;'''
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        return {id:type for id, type in cursor}

def get_id_to_geometry():
    cursor = connection.cursor()
    cursor.execute('''
    SELECT link_id, geom, geom_dist, geom_orig FROM link_geometry;
    ''')
    return {id: GEOSGeometry(geom_orig) for id, geom, geom_dist, geom_orig in cursor}
class LinkFilter:
    def __init__(self, include, idtotypemap):
        self.include =set(include)
        self.idtotypemap = idtotypemap

    def filter(self, ids):
        return [id for id in ids if self.idtotypemap[id] in self.include]

class LAFilter:
    def __init__(self, idtogeom):
        self.idtogeom = idtogeom
        self.labb = Polygon.from_bbox((-118.3836263,33.930957, -118.2309,34.0748))
    def filter(self, ids):
        return [id for id in ids if not self.labb.intersects(self.idtogeom[id])]

def create_routes():
    link_types = ['"motorway"']
    lf = LAFilter(get_id_to_geometry())
    rl = RouteLoader(lambda : RouteCreator(config.SIMILARITY_FACTOR), connection, 'filtered_routes', lambda x: lf.filter(x))
    rl.import_link_geometry_table()
    rl.load_routes()


def waypoint_od_bins():
    import os;
    os.system("psql -U megacell -d geodjango -f experiments/experiment2/database_setup/create_od_waypoint_view_filtered_routes.sql")

#create_routes()
#waypoint_od_bins()
run_experiment.get_phi(True)
run_experiment.generate_experiment_matrices()