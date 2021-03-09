from django.conf.urls import url
from ticketing import views

app_name = "ticketing"

urlpatterns = [
    url('^ticketing/$', views.index,
        name='index'),
    url(r'^ticketing/ticket_items/$', views.ticket_items,
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
    url(r'^ticketing/set_ticket_to_event/(?P<bpt_event_id>\d+)/' +
        '(?P<state>on|off)/(?P<gbe_eventitem_id>\d+)/?$',
        views.set_ticket_to_event,
        name='set_ticket_to_event'),
]
