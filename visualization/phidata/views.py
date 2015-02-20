from django.shortcuts import render
from rest_framework import generics
import models
from serializers import LinkSerializer, LinkFlowSerializer, RouteSerializer

# Create your views here.
class LinkList(generics.ListAPIView):
    queryset = models.Link.objects.all()
    serializer_class = LinkSerializer

class LinkFlowList(generics.ListAPIView):
    queryset = models.LinkFlow.objects.all()
    serializer_class = LinkFlowSerializer

class RouteList(generics.ListAPIView):
    queryset = models.Route.objects.all()
    serializer_class = RouteSerializer

