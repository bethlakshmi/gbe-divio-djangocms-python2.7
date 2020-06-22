#
# models.py - Contains Django code for defining the URL structure for ticketing
# edited by mdb 5/9/2014
# edited by bb 7/27/2015
#

from django.conf.urls import url
from ticketing import views

app_name = "ticketing"

urlpatterns = [
    url('^ticketing/$', views.index,
        name='index'),
    url(r'^ticketing/ticket_items/$', views.ticket_items,
        name='ticket_items'),
    url(r'^ticketing/ticket_items/?$', views.ticket_items,
        name='ticket_items'),
    url(r'^ticketing/ticket_item_edit/?$', views.ticket_item_edit,
        name='ticket_item_edit'),
    url(r'^ticketing/ticket_item_edit/(?P<item_id>\d+)/?$',
        views.ticket_item_edit,
        name='ticket_item_edit'),
    url(r'^ticketing/bptevent_edit/?$', views.bptevent_edit,
        name='bptevent_edit'),
    url(r'^ticketing/bptevent_edit/(?P<event_id>\d+)/?$', views.bptevent_edit,
        name='bptevent_edit'),
    url(r'^ticketing/transactions/?$', views.transactions,
        name='transactions'),
]
