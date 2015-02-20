__author__ = 'lei'
from models import Link, LinkFlow
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

    def load(self):
        for id, line in enumerate(self.lines):
            l = Link(id=id,geom=MultiLineString(LineString(line)))
            l.save()

class DummyLinkFlows:
    def __init__(self):
        self.flow_type ="test"

    def clear(self):
        LinkFlow.objects.all().delete()

    def load(self):
        for id, link in enumerate(Link.objects.all()):
            l = LinkFlow(link_id=link, flow=id*10, flow_type=self.flow_type)
            l.save()
