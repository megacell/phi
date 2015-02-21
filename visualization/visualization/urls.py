from django.conf.urls import patterns, url

from phidata import views as phi_views
from client import views as client_views

urlpatterns = patterns('',
    url(r'^$', client_views.visualization_page),
    url(r'^phidata/links/?$', phi_views.LinkList.as_view()),
    url(r'^phidata/links/(?P<pk>[0-9]+)/?', phi_views.LinkList.as_view()),
    url(r'^phidata/flows/?$', phi_views.LinkFlowList.as_view()),
    url(r'^phidata/linktable/(?P<link_id>\d+)/?$', phi_views.LinkRoutesList.as_view()),
    url(r'^phidata/cells/?$', phi_views.CellList.as_view()),
    url(r'^phidata/cells/(?P<cellidlist>.+)/$', phi_views.CellActiveLinkList.as_view()),

)
