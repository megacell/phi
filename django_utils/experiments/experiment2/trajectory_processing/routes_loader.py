from django_utils.orm.models import Experiment2Route
import pickle
import django_utils.config as config
from django.contrib.gis.geos import MultiLineString
from django.db import transaction

def wrapLineInMultiLine(g):
    if type(g) == MultiLineString:
        return g
    else:
        return MultiLineString(g)

def print_unique_links():
    routes = pickle.load(open('data.pkl'))
    print(len(routes))
    links = set()
    for r in routes:
        links.update(r._trajectory._id_sequence)
    print("Number of unique links in routes used: " +  str(len(links)))

#@transaction.atomic
def import_to_db():
    routes = pickle.load(open('data.pkl'))

    Experiment2Route.objects.all().delete()
    print(len(routes))
    for id, route in enumerate(routes):

        original_geom = wrapLineInMultiLine(route._trajectory.convert_to_LineString())
        original_geom.set_srid(config.EPSG32611)

        geom_dist = original_geom.clone()
        geom_dist.transform(config.google_projection)

        geom = original_geom.clone()
        geom.transform(config.canonical_projection)

        o, d = route.od_taz_id

        start = route._trajectory._start_point.clone()
        start.set_srid(config.EPSG32611)
        start.transform(config.canonical_projection)

        end = route._trajectory._end_point.clone()
        end.set_srid(config.EPSG32611)
        end.transform(config.canonical_projection)

        e2r = Experiment2Route(
            geom=geom,
            geom_dist=geom_dist,
            origin_taz=o,
            destination_taz=d,
            od_route_index=id,
            flow_count=route._agent_count,
            start_point=start,
            end_point=end
            )
        e2r.save()
