# ticketing_idd.py - Interface Design Description (IDD) between GBE and
# TICKETING modules

# See documentation in https://github.com/bethlakshmi/GBE2/wiki/Ticketing-To-Do
# section:  "By Friday - needed for integration"
# - Betty 8/15
from gbe_logging import logger
from ticketing.models import (
    BrownPaperEvents,
    RoleEligibilityCondition,
    TicketingEligibilityCondition,
    TicketItem,
    Transaction,
)
from ticketing.forms import (
    DonationForm,
    TicketPayForm,
)
from gbe.models import (
    Conference,
)
from scheduler.idd import get_roles
from ticketing.brown_paper import *
from gbetext import (
    payment_details_error,
)
from django.db.models import Count
from ticketing.views import import_ticket_items
from django.db.models import Q
from datetime import datetime
from django.forms import HiddenInput
from django.core.validators import MinValueValidator


def performer_act_submittal_link(user_id):
    '''
    defines the act submission url for BPT to be used for payment.
    In other words, this gives you a string that a given user should go
    to at BPT to pay the fee.
    user_id - the integer User ID of the user.
    returns - the URL string described above.
    '''
    act_sub_events = BrownPaperEvents.objects.filter(
        act_submission_event=True,
        conference=Conference.objects.filter(status="upcoming").first())
    if (act_sub_events.count() > 0):
        return ('http://www.brownpapertickets.com/event/ID-' +
                str(user_id) +
                '/' +
                act_sub_events[0].bpt_event_id)
    return None


def vendor_submittal_link(user_id):
    '''
    defines the vendor url for BPT to be used for payment.  In other words,
    this gives you a string that a given user should go to at BPT to pay the
    fee.
    user_id - the integer User ID of the user.
    returns - the URL string described above.
    '''
    vendor_events = BrownPaperEvents.objects.filter(
        vendor_submission_event=True,
        conference=Conference.objects.filter(status="upcoming").first())
    if (vendor_events.count() > 0):
        return ('http://www.brownpapertickets.com/event/ID-' +
                str(user_id) +
                '/' +
                vendor_events[0].bpt_event_id)
    return None


def verify_performer_app_paid(user_name, conference):
    '''
    Verifies if a user has paid his or her application fee.
    NOTE:  This function assumes that there is a record of the application,
    saved in the database with a status of "submitted", at the time the check
    is performed.
    user_name - This is the user name of the user in question.
    returns - true if the system recognizes the application submittal fee is
      paid
    '''
    from gbe.models import Act
    acts_submitted = 0
    # First figure out how many acts this user has purchased
    act_fees_purchased = Transaction.objects.filter(
        ticket_item__bpt_event__act_submission_event=True,
        ticket_item__bpt_event__conference=conference,
        purchaser__matched_to_user__username=str(user_name)).count()
    # Then figure out how many acts have already been submitted.
    acts_submitted = Act.objects.filter(
        submitted=True,
        b_conference=conference,
        performer__contact__user_object__username=user_name).count()

    logger.info("Purchased Count:  %s  Submitted Count:  %s" %
                (act_fees_purchased, acts_submitted))
    return act_fees_purchased > acts_submitted


def verify_vendor_app_paid(user_name, conference):
    '''
    Verifies user has paid a vendor submittal fee.
    NOTE:  This function assumes that there is a record of the application,
    saved in the database, with a status of "submitted", at the time the check
    is performed.
    user_name - This is the user name of the user in question.
    returns - true if the system recognizes the vendor submittal fee is paid
    '''
    from gbe.models import Vendor
    vendor_fees_purchased = 0
    vendor_apps_submitted = 0

    # First figure out how many vendor spots this user has purchased
    for vendor_event in BrownPaperEvents.objects.filter(
            vendor_submission_event=True,
            conference=conference):
        for trans in Transaction.objects.all():
            trans_event = trans.ticket_item.ticket_id.split('-')[0]
            trans_user_name = trans.purchaser.matched_to_user.username

            if ((vendor_event.bpt_event_id == trans_event) and
                    (str(user_name) == trans_user_name)):
                vendor_fees_purchased += 1

    # Then figure out how many vendor applications have already been submitted.
    vendor_apps_submitted = Vendor.objects.filter(
        submitted=True,
        b_conference=conference,
        profile__user_object__username=user_name).count()
    logger.info("Purchased Count:  %s  Submitted Count:  %s" %
                (vendor_fees_purchased, vendor_apps_submitted))
    return vendor_fees_purchased > vendor_apps_submitted


def verify_bought_conference(user, conference):
    return TicketItem.objects.filter(
        Q(bpt_event__conference=conference),
        Q(transaction__purchaser__matched_to_user=user),
        Q(bpt_event__include_conference=True) | Q(bpt_event__include_most=True)
        ).exists()


def get_purchased_tickets(user):
    '''
    get the tickets purchased by the given profile
    '''
    ticket_by_conf = []
    conferences = Conference.objects.exclude(
        status="completed").order_by('status')
    for conf in conferences:
        tickets = TicketItem.objects.filter(
            bpt_event__conference=conf,
            transaction__purchaser__matched_to_user=user).annotate(
                number_of_tickets=Count('transaction')).order_by('title')
        if tickets:
            ticket_by_conf.append({'conference': conf, 'tickets': tickets})
    return ticket_by_conf


def get_checklist_items_for_tickets(profile,
                                    conference,
                                    tickets):
    '''
    get the checklist items for a purchaser in the BTP
    '''
    checklist_items = []
    transactions = Transaction.objects.filter(
            purchaser__matched_to_user=profile.user_object)

    for ticket in set(tickets):
        items = []
        count = transactions.filter(ticket_item=ticket).count()
        if count > 0:
            for condition in TicketingEligibilityCondition.objects.filter(
                    tickets=ticket):
                if not condition.is_excluded(tickets, profile, conference):
                    items += [condition.checklistitem]
            if len(items) > 0:
                checklist_items += [{'ticket': ticket.title,
                                     'count': count,
                                     'items': items}]

    return checklist_items


def get_checklist_items_for_roles(profile, conference, tickets):
    '''
    get the checklist items for the roles a person does in this conference
    '''
    checklist_items = {}

    roles = get_roles(profile.user_object,
                      labels=[conference.conference_slug]).roles
    for condition in RoleEligibilityCondition.objects.filter(role__in=roles):
        if not condition.is_excluded(tickets, profile, conference):
            if condition.role in checklist_items:
                checklist_items[condition.role] += [condition.checklistitem]
            else:
                checklist_items[condition.role] = [condition.checklistitem]
    return checklist_items


def get_checklist_items(profile, conference):
    '''
    get the checklist items for a person with a profile
    '''
    tickets = TicketItem.objects.filter(
        bpt_event__conference=conference,
        transaction__purchaser__matched_to_user=profile.user_object).distinct()

    ticket_items = get_checklist_items_for_tickets(profile,
                                                   conference,
                                                   tickets)

    role_items = get_checklist_items_for_roles(profile,
                                               conference,
                                               tickets)

    return (ticket_items, role_items)


def create_bpt_event(bpt_event_id, conference, events=[], display_icon=None):
    event = BrownPaperEvents.objects.create(
            bpt_event_id=bpt_event_id,
            conference=conference,
            display_icon=display_icon)
    if len(events) > 0:
        event.linked_events.add(*events)
    event.save()
    count = import_ticket_items([event])
    return event, count


def get_ticket_list(bid_type, conference):
    ticket_items = TicketItem.objects.filter(
        bpt_event__conference=conference, live=True, has_coupon=False).exclude(
        start_time__lt=datetime.now(), end_time__gt=datetime.now())
    if bid_type == "Vendor":
        ticket_items = ticket_items.filter(
            bpt_event__vendor_submission_event=True)
    elif bid_type == "Act":
        ticket_items = ticket_items.filter(
            bpt_event__act_submission_event=True)
    else:
        raise Exception("Invalid Bid Type: %s" % bid_type)
    return ticket_items


def get_ticket_form(bid_type, conference):
    form = None
    ticket_items = get_ticket_list(bid_type, conference)

    if ticket_items.filter(is_minimum=True).exists():
        minimum = ticket_items.filter(is_minimum=True).order_by(
            'cost').first().cost
        form = DonationForm(initial={'donation_min': minimum,
                                     'donation': minimum})
    else:
        form = TicketPayForm()
        form.fields['main_ticket'].queryset = ticket_items.filter(
            add_on=False).order_by('cost')
        if ticket_items.filter(add_on=True).exists():
            form.fields['add_ons'].queryset = ticket_items.filter(
                add_on=True).order_by('cost')
        else:
            form.fields['add_ons'].widget = HiddenInput()

    return form

def get_payment_details(post, bid_type, conference):
    cart = []
    paypal_button = None
    form = None
    ticket_items = get_ticket_list(bid_type, conference)
    if ticket_items.filter(is_minimum=True).exists():
        minimum = ticket_items.filter(is_minimum=True).order_by(
            'cost').first().cost
        form = DonationForm(post, initial={'donation_min': minimum,
                                     'donation': minimum})
    else:
        form = TicketPayForm(post)
        form.fields['main_ticket'].queryset = ticket_items.filter(
            add_on=False).order_by('cost')
        if ticket_items.filter(add_on=True).exists():
            form.fields['add_ons'].queryset = ticket_items.filter(
                add_on=True).order_by('cost')
        else:
            form.fields['add_ons'].widget = HiddenInput()
    if form.is_valid():
        return cart, paypal_button
    else:
        raise Exception(
            form,
            'PAYMENT_CHOICE_INVALID', 
            "User Made Invalid Ticket Choice",
            payment_details_error)
