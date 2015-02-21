__author__ = 'lei'
from phidata.models import Link, LinkFlow, Route
from django.contrib.gis.geos import LineString, MultiLineString

class DummyLinks:
    def __init__(self):
        self.lines = [
            [[-118.308914, 33.974394],
            [-118.300266, 33.974465],
            [-118.291554, 33.974465],
            [-118.281169, 33.974572],],

            [[-118.309107, 33.981862],
            [-118.300266, 33.982146],
            [-118.291168, 33.982075],
            [-118.28104 , 33.982075],],

            [[-118.309021, 33.988979],
            [-118.300266, 33.988836],
            [-118.291426, 33.988907],
            [-118.280783, 33.988694],],

            [[-118.308935, 33.996806],
            [-118.300095, 33.996664],
            [-118.291855, 33.996735],
            [-118.280525, 33.996806],],]
    def clear(self):
        Link.objects.all().delete()
        return self

    def load(self):
        for id, line in enumerate(self.lines):
            l = Link(id=id,geom=MultiLineString(LineString(line)))
            l.save()
        return self

class DummyLinkFlows:
    def __init__(self):
        self.flow_type ="test"

    def clear(self):
        LinkFlow.objects.all().delete()
        return self
    def load(self):
        for id, link in enumerate(Link.objects.all()):
            l = LinkFlow(link_id=link, flow=id*10, flow_type=self.flow_type)
            l.save()
        return self

class DummyRoutes:
    def clear(self):
        Route.objects.all().delete()
        return self

    def load(self):
        routes = [[0,1],[1,2],[2,3]]
        for id, route in enumerate(routes):
            r = Route(id=id, links=route)
            r.save()
        return self

if __name__ == "__main__":
    DummyLinks().clear().load()
    DummyLinkFlows().clear().load()
    DummyRoutes().clear().load()
