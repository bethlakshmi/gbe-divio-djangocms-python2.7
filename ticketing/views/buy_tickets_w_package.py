from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from ticketing.models import (
    TicketPackage,
    TicketType,
)
from gbe_utils.mixins import GbeContextMixin
from gbe.models import UserMessage
from gbetext import purchase_intro_msg
from datetime import datetime


class TicketAndPackageList(GbeContextMixin, ListView):
    # ticket list for purchasers (public) based on Humanitix types & packages
    model = TicketPackage
    template_name = 'ticketing/purchase_tickets_and_packages.tmpl'
    context_object_name = 'packages'
    queryset = TicketPackage.objects.filter(
        live=True,
        has_coupon=False,
        ticketing_event__act_submission_event=False,
        ticketing_event__vendor_submission_event=False,
        ).exclude(ticketing_event__conference__status='completed')
    page_title = 'Buy Tickets'
    view_title = 'Ticket Purchase Options for Great Burlesque Expo'
    intro_text = purchase_intro_msg

    def get_context_data(self, **kwargs):
        # TODO - figure out how to exclude dates if dates are tehre
        context = super().get_context_data(**kwargs)
        tickets = TicketType.objects.filter(
            live=True,
            has_coupon=False,
            ticketing_event__act_submission_event=False,
            ticketing_event__vendor_submission_event=False,
            ).exclude(ticketing_event__conference__status='completed')
        events = {}
        for ticket in tickets:
            for gbe_event in ticket.linked_events.all():
                if gbe_event in events.keys():
                    if events[gbe_event]['min_price'] > ticket.cost:
                        events[gbe_event]['min_price'] = ticket.cost
                    if events[gbe_event]['max_price'] < ticket.cost:
                        events[gbe_event]['max_price'] = ticket.cost
                        events[gbe_event]['expensive_ticket'] = ticket
                else:
                    events[gbe_event] = {
                    'min_price': ticket.cost,
                    'max_price': ticket.cost,
                    'ticket_event': ticket.ticketing_event,
                    'expensive_ticket': ticket}
        context['events'] = events
        context['user_id'] = self.request.user.id,
        return context
