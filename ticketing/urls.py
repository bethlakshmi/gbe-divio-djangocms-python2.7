from django.conf.urls import url
from ticketing import views
from ticketing.views import (
    BadgePrintView,
    CheckListItemList,
    CreateTransaction,
    TicketPackageUpdate,
    TicketTypeUpdate,
)

app_name = "ticketing"

urlpatterns = [
    url('^ticketing/original/$',
        views.index,
        name='index'),
    url(r'^ticketing/ticket_items/$', views.ticket_items,
        name='ticket_items'),
    url(r'^ticketing/ticket_item_edit/?$', views.ticket_item_edit,
        name='ticket_item_edit'),
    url(r'^ticketing/ticket_item_edit/(?P<item_id>\d+)/?$',
        views.ticket_item_edit,
        name='ticket_item_edit'),
    url(r'^ticketing/ticket_package_update/(?P<pk>.*)/?$',
        TicketPackageUpdate.as_view(),
        name='ticket_package_update'),
    url(r'^ticketing/ticket_type_update/(?P<pk>.*)/?$',
        TicketTypeUpdate.as_view(),
        name='ticket_type_update'),
    url(r'^ticketing/ticket_event_edit/?$', views.ticket_event_edit,
        name='bptevent_edit'),
    url(r'^ticketing/ticket_event_edit/(?P<event_id>\d+)/?$',
        views.ticket_event_edit,
        name='bptevent_edit'),
    url(r'^ticketing/transactions/?$', views.transactions,
        name='transactions'),
    url(r'^ticketing/transaction/create/?$',
        CreateTransaction.as_view(),
        name='comp_ticket'),
    url(r'^sign_forms/?$',
        CreateTransaction.as_view(),
        name='sign_forms'),
    url(r'^ticketing/checklist/?$',
        CheckListItemList.as_view(),
        name='checklistitem_list'),
    url(r'^ticketing/badges/?$',
        BadgePrintView.as_view(),
        name='badge_print'),
    url(r'^ticketing/set_ticket_to_event/(?P<pk>.*)/(?P<ticket_class>\w+)/' +
        '(?P<state>on|off)/(?P<gbe_event_id>\d+)/?$',
        views.set_ticket_to_event,
        name='set_ticket_to_event'),
    url(r'^ticketing/set_ticket_type_to_event/(?P<pk>.*)/' +
        '(?P<state>on|off)/(?P<gbe_event_id>\d+)/?$',
        views.set_ticket_to_event,
        name='set_ticket_type_to_event'),
]
