# ticketing_idd.py - Interface Design Description (IDD) between GBE and
# TICKETING modules

# See documentation in https://github.com/bethlakshmi/GBE2/wiki/Ticketing-To-Do
# section:  "By Friday - needed for integration"
# - Betty 8/15
from gbe_logging import logger
from ticketing.models import (
    Purchaser,
    TicketingEvents,
    PayPalSettings,
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
from ticketing.brown_paper import *
from ticketing.functions import get_fee_list
from ticketing.brown_paper import import_bpt_ticket_items
from django.db.models import Count
from django.db.models import Q
from datetime import datetime
from django.forms import HiddenInput
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse


def fee_paid(bid_type, user_name, conference):
    if bid_type == "Act":
        return verify_performer_app_paid(user_name, conference)
    elif bid_type == "Vendor":
        return verify_vendor_app_paid(user_name, conference)
    return True


def comp_act(user, conference):
    if not TicketItem.objects.filter(
            add_on=False,
            ticketing_event__act_submission_event=True,
            ticketing_event__conference=conference).exists():
        return False
    comp_ticket = TicketItem.objects.filter(
        add_on=False,
        ticketing_event__act_submission_event=True,
        ticketing_event__conference=conference).first()
    purchaser = Purchaser(
        matched_to_user=user,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email)
    purchaser.save()
    transaction = Transaction(
        purchaser=purchaser,
        ticket_item=comp_ticket,
        amount=0,
        order_date=datetime.now(),
        shipping_method="Comp'ed",
        order_notes="Comped through IDD",
        reference="auto",
        payment_source="GBE")
    transaction.save()
    return True


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
        ticket_item__add_on=False,
        ticket_item__ticketing_event__act_submission_event=True,
        ticket_item__ticketing_event__conference=conference,
        purchaser__matched_to_user__username=str(user_name)).count()
    # Then figure out how many acts have already been submitted.
    acts_submitted = Act.objects.filter(
        submitted=True,
        b_conference=conference,
        bio__contact__user_object__username=user_name).count()

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
    vendor_apps_submitted = 0

    # First figure out how many vendor spots this user has purchased
    vendor_fees_purchased = Transaction.objects.filter(
            ticket_item__add_on=False,
            ticket_item__ticketing_event__vendor_submission_event=True,
            ticket_item__ticketing_event__conference=conference,
            purchaser__matched_to_user__username=str(user_name)).count()

    # Then figure out how many vendor applications have already been submitted.
    vendor_apps_submitted = Vendor.objects.filter(
        submitted=True,
        b_conference=conference,
        business__owners__user_object__username=user_name).count()
    logger.info("Purchased Count:  %s  Submitted Count:  %s" %
                (vendor_fees_purchased, vendor_apps_submitted))
    return vendor_fees_purchased > vendor_apps_submitted


def verify_bought_conference(user, conference_slugs):
    return TicketItem.objects.filter(
        Q(ticketing_event__conference__conference_slug__in=conference_slugs),
        Q(transaction__purchaser__matched_to_user=user),
        Q(ticketing_event__include_conference=True) | Q(
            ticketing_event__include_most=True)
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
            ticketing_event__conference=conf,
            transaction__purchaser__matched_to_user=user).annotate(
                number_of_tickets=Count('transaction')).order_by('title')
        if tickets:
            ticket_by_conf.append({'conference': conf, 'tickets': tickets})
    return ticket_by_conf


def get_checklist_items_for_tickets(profile, user_schedule, tickets):
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
                if not condition.is_excluded(tickets, user_schedule):
                    items += [condition.checklistitem]
            if len(items) > 0:
                checklist_items += [{'ticket': ticket.title,
                                     'count': count,
                                     'items': items}]

    return checklist_items


def get_checklist_items_for_roles(user_schedule, tickets):
    '''
    get the checklist items for the roles a person does in this conference
    '''
    checklist_items = {}

    roles = []
    for booking in user_schedule:
        if booking.role not in roles:
            roles += [booking.role]

    for condition in RoleEligibilityCondition.objects.filter(role__in=roles):
        if not condition.is_excluded(tickets, user_schedule):
            if condition.role in checklist_items:
                checklist_items[condition.role] += [condition.checklistitem]
            else:
                checklist_items[condition.role] = [condition.checklistitem]
    return checklist_items


def get_checklist_items(profile, conference, user_schedule):
    '''
    get the checklist items for a person with a profile
    '''
    tickets = TicketItem.objects.filter(
        ticketing_event__conference=conference,
        transaction__purchaser__matched_to_user=profile.user_object).distinct()

    ticket_items = get_checklist_items_for_tickets(
        profile,
        user_schedule,
        tickets)

    role_items = get_checklist_items_for_roles(user_schedule, tickets)

    return (ticket_items, role_items)


def get_ticket_form(bid_type, conference, post=None):
    form = None
    ticket_items = get_fee_list(bid_type, conference)

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

    return form


def get_paypal_button(request, total, user_id, number_list, bid_type, bid_id):
    paypal_dict = {
        "business": PayPalSettings.objects.first().business_email,
        "amount": total,
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "invoice": str(datetime.now()),
        "custom": "%s-%d-User-%d" % (bid_type, bid_id, user_id),
        "return": request.build_absolute_uri(
            reverse(
                "%s_view" % bid_type.lower(),
                urlconf='gbe.urls',
                args=[bid_id])),
        "cancel_return": request.build_absolute_uri("%s?cancel=paypal" % (
            reverse(
                "%s_edit" % bid_type.lower(),
                urlconf='gbe.urls',
                args=[bid_id]))),
        "item_name": "%s Fee(s)" % bid_type,
        "item_number": number_list,
    }
    return PayPalPaymentsForm(initial=paypal_dict)


def get_payment_details(request, form, bid_type, bid_id, user_id):
    cart = []
    paypal_button = None
    total = 0
    minimum = None
    main_ticket = None
    number_list = ""

    if 'donation' in list(form.cleaned_data.keys()):
        cart += [("%s Submission Fee" % bid_type,
                  form.cleaned_data['donation'])]
        total = total + form.cleaned_data['donation']
    else:
        cart += [(form.cleaned_data['main_ticket'].title,
                  form.cleaned_data['main_ticket'].cost)]
        number_list = str(form.cleaned_data['main_ticket'].id)
        total = total + form.cleaned_data['main_ticket'].cost
        for item in form.cleaned_data['add_ons']:
            cart += [(item.title, item.cost)]
            number_list = "%s %d" % (number_list, item.id)
            total = total + item.cost
    return (
        cart,
        get_paypal_button(
            request,
            total,
            user_id,
            number_list,
            bid_type,
            bid_id),
        total)
