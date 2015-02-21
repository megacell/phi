from django.shortcuts import render
from rest_framework import generics
import models
from serializers import LinkSerializer, LinkFlowSerializer, LinkTableSerializer, CellSerializer

# Create your views here.
class LinkList(generics.ListAPIView):
    queryset = models.Link.objects.all()
    serializer_class = LinkSerializer

class LinkFlowList(generics.ListAPIView):
    queryset = models.LinkFlow.objects.all()
    serializer_class = LinkFlowSerializer

class LinkRoutesList(generics.ListAPIView):
    def get_queryset(self):
        link_id = self.kwargs['link_id']
        s = set()
        for r in models.Route.objects.raw('select id, links from phidata_route where %s = any(links);', [link_id]):
            s.update(r.links)
        return [models.LinkTable(link_id, s)]
    serializer_class = LinkTableSerializer

class CellList(generics.ListAPIView):
    queryset =  models.Cell.objects.all()
    serializer_class = CellSerializer

class CellActiveLinkList(generics.ListAPIView):
    def get_queryset(self):
        cellset = self.kwargs['cellidlist']
        cellset = cellset.strip('[]')
        cellset = cellset.split(',')
        if len(cellset) == 0 or len(cellset[0]) == 0:
            return [models.LinkTable(0, [l.id for l in list(models.Link.objects.all())])]
        cellset =  map(int, cellset)

        sql_query = '''select cr.id, cr.routes
        from phidata_cellroutemap cr,
        (
            select p.id, p.geom
            from
            (
                    select unnest(Array{0}) as id
            ) s
            join phidata_cell p
            on s.id = p.id
        ) c
            where c.id = cr.id;'''.format('[' +','.join(map(str,cellset)) +']')
        result = None
        for cr in models.CellRouteMap.objects.raw(sql_query):
            if result is None:
                result = set(cr.routes)
            result.intersection_update(cr.routes)
            if len(result) == 0:
                break
        links = set()
        if result == None:
            return [models.LinkTable(0, [])]
        for r in result:
            route = models.Route.objects.filter(id=r).first()
            links.update(route.links)

        return [models.LinkTable(0, list(links))]

    serializer_class = LinkTableSerializer