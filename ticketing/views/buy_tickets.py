from django.shortcuts import render, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from ticketing.models import (
    TicketingEvents,
    TicketItem,
)
from gbe.models import UserMessage
from gbetext import purchase_intro_msg
from django.db.models import (
    Max,
    Min,
    Q,
)


def index(request):
    '''
    Represents the view for the main screen.  This will eventually be the
    equivalent of cost.php from the old site.
    '''
    ''' Query means - get upcoming/current conference BPT events, annotate
      with a max and min price but only for the public tickets (not comps,
      not discounts), then sort by conference and descending highest price.
      The first thing on the list should be the whole weekend ticket, for the
      soonest conference.'''
    events = TicketingEvents.objects.exclude(
        Q(conference__status='completed') | Q(
            act_submission_event=True) | Q(
            vendor_submission_event=True)).annotate(
            max_price=Max('ticketitems__cost',
                          filter=Q(ticketitems__live=True,
                                   ticketitems__has_coupon=False))).annotate(
            min_price=Min('ticketitems__cost',
                          filter=Q(ticketitems__live=True,
                                   ticketitems__has_coupon=False))).order_by(
        'conference__conference_slug', '-max_price', '-min_price')
    intro = UserMessage.objects.get_or_create(
            view="ListPublicTickets",
            code="INTRO_MESSAGE",
            defaults={
                'summary': "Intro at top of list",
                'description': purchase_intro_msg})
    context = {'events': events,
               'user_id': request.user.id,
               'site_name': get_current_site(request).name,
               'introduction': intro[0].description
               }
    return render(request, 'ticketing/purchase_tickets.tmpl', context)
