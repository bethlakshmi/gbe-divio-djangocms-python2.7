#
# brown_paper.py - Contains Functions for Integration with Brown Paper Tickets
# edited by mdb 8/18/2014
#
#

from gbe_logging import logger
import urllib
from django.utils import timezone
import xml.etree.ElementTree as et
from django.contrib.auth.models import User
from ticketing.models import (
    TicketingEvents,
    BrownPaperSettings,
    Purchaser,
    TicketItem,
    Transaction,
)
import html
from django.utils import timezone
from gbe.models import Profile
import sys
from datetime import datetime
import pytz


def import_bpt_ticket_items(events=None):
    '''
    Function is used to initiate an import from BPT or other sources of
    new Ticket Items.  It will not override existing items.
    '''
    if BrownPaperSettings.objects.exists():
        settings = BrownPaperSettings.objects.first()
        if not settings.active_sync:
            return 0
    import_item_list = get_bpt_price_list(events)

    for i_item in import_item_list:
        ticket_item, created = TicketItem.objects.get_or_create(
            ticket_id=i_item['ticket_id'],
            defaults=i_item)
        if not created:
            ticket_item.modified_by = 'BPT Import'
            ticket_item.live = i_item['live']
            ticket_item.cost = i_item['cost']
            ticket_item.save()
    return len(import_item_list)


def perform_bpt_api_call(api_call):
    '''
    Used to make various calls to the Brown Paper Tickets API system.
    event_call - the API call to be performed.

    Returns: a Simple XML element tree or None for an error.
    '''

    try:
        req = urllib.request.Request(api_call)
        req.add_header('Accept', 'application/json')
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        res = urllib.request.urlopen(req)
        xml_tree = et.fromstring(res.read())
    except urllib.error.URLError as io_error:
        logger.error('Could not perform BPT call:  %s' % io_error.reason)
        return None
    except:
        logger.error(
            'Could not perform BPT call.  Reason: %s ' % (sys.exc_info()[0]))
        return None
    return xml_tree


def get_bpt_developer_id():
    '''
    Used to obtain the developer token to be used with Brown Paper Tickets.

    Returns: the developer token, or None if none exists.
    '''
    if BrownPaperSettings.objects.exists():
        settings = BrownPaperSettings.objects.first()
        return settings.developer_token
    return None


def get_bpt_client_id():
    '''
    Used to obtain the client username to be used with Brown Paper Tickets.

    Returns: the client username, or None if none exists.
    '''
    if BrownPaperSettings.objects.exists():
        settings = BrownPaperSettings.objects.first()
        return settings.client_username
    return None


def set_bpt_last_poll_time():
    '''
    Used to set the last time the system poled BPT for transactions
    to current time.

    Returns: None
    '''
    if BrownPaperSettings.objects.exists():
        settings = BrownPaperSettings.objects.first()
        settings.last_poll_time = timezone.now()
        settings.save()
    return None


def set_bpt_event_detail(event):
    '''
    Given the bpt event, this queries BPT and gets the title & description
    and sets them in the GBE database.  It only does this once, to avoid over
    writing changes made in GBE
    '''

    if event.title and len(event.title) > 0:
        return

    url = "?".join(['http://www.brownpapertickets.com/api2/eventlist',
                    'id=%s&client=%s&event_id=%s'])
    event_call = url % (get_bpt_developer_id(),
                        get_bpt_client_id(),
                        event.event_id)
    event_xml = perform_bpt_api_call(event_call)
    if event_xml is None:
        return None

    event.title = html.unescape(event_xml.find('.//title').text)
    event.description = html.unescape(event_xml.find('.//e_description').text)
    event.save()


def get_bpt_event_date_list(event_id):
    '''
    Used to get the list of date identifiers from the BPT website for
    the given event.

    event_id - the event id for the event to query
    Returns: the date list requested, as a python list.
    '''
    url = "?".join(['http://www.brownpapertickets.com/api2/datelist',
                    'id=%s&event_id=%s'])
    date_call = url % (get_bpt_developer_id(), event_id)
    date_xml = perform_bpt_api_call(date_call)

    if date_xml is None:
        return []

    date_list = []
    for date in date_xml.findall('.//date_id'):
        date_list.append(date.text)
    return date_list


def get_bpt_price_list(ticketing_events=None):
    '''
    Used to get the list of prices from BPT - which directly relates to
    ticket items on our system.

    Returns: the price list as an array of TicketItems.
    '''
    ti_list = []

    if not ticketing_events:
        ticketing_events = TicketingEvents.objects.exclude(
            conference__status="completed").filter(source=1)
    for event in ticketing_events:
        set_bpt_event_detail(event)

        for date in get_bpt_event_date_list(event.event_id):
            url = "?".join(
                ['http://www.brownpapertickets.com/api2/pricelist',
                 'id=%s&event_id=%s&date_id=%s'])
            price_call = url % (get_bpt_developer_id(),
                                event.event_id,
                                date)
            price_xml = perform_bpt_api_call(price_call)

            if price_xml is not None:
                for price in price_xml.findall('.//price'):
                    ti_list.append(
                        bpt_price_to_ticketitem(event, price))

    return ti_list


def bpt_price_to_ticketitem(event, bpt_price):
    '''
    Function takes an XML price object from the BPT pricelist call and returns
    an equivalent dictionary that is appropriate to the TicketItem object.

    event_id - the Event ID associated with this price
    bpt_price - the price object from the BPT call
    event_text - Text that describes the event from BPT
    Returns:  the TicketItem dictionary
    '''
    live = False
    if bpt_price.find('live').text == 'y':
        live = True
    t_item = {
        'ticket_id': '%s-%s' % (event.event_id,
                                bpt_price.find('price_id').text),
        'title': bpt_price.find('name').text,
        'cost': bpt_price.find('value').text,
        'modified_by': 'BPT Auto Import',
        'ticketing_event': event,
        'live': live,
    }

    return t_item


def process_bpt_order_list():
    '''
    Used to get the list of current orders in the BPT database and update the
    transaction table accordingly.

    Returns: the number of transactions imported.
    '''
    if BrownPaperSettings.objects.exists():
        settings = BrownPaperSettings.objects.first()
        if not settings.active_sync:
            return 0

    count = 0

    # Process the list from Brown Paper Tickets
    dev_id = get_bpt_developer_id()
    client_id = get_bpt_client_id()
    for event in TicketingEvents.objects.exclude(
            conference__status='completed').filter(source=1):
        url = "?".join(['http://www.brownpapertickets.com/api2/orderlist',
                        'id=%s&event_id=%s&account=%s&includetracker=1'])
        order_list_call = url % (dev_id,
                                 event.event_id,
                                 client_id)
        order_list_xml = perform_bpt_api_call(order_list_call)
        if order_list_xml is not None:
            for bpt_order in order_list_xml.findall('.//item'):
                ticket_number = bpt_order.find('ticket_number').text

                if not (transaction_reference_exists(ticket_number)):
                    if bpt_save_order_to_database(event.event_id, bpt_order):
                        count += 1

    # Recheck to see if any emails match to users now.  For example, if
    # a new user created a profile after purchasing a ticket.

    match_existing_purchasers_using_email()

    if count > 0:
        set_bpt_last_poll_time()
    return count


def match_existing_purchasers_using_email():
    '''
    Function goes through all of the purchasers in the system, and if
    the purchasers is currently set to the "limbo" user (indicating
    purchaser is not linked to a real user yet) we attempt
    to match it.

    returns None
    '''

    for purchaser in Purchaser.objects.filter(
            matched_to_user__username='limbo'):
        matched_user = attempt_match_purchaser_to_user(purchaser)
        if matched_user is not None:
            purchaser.matched_to_user = matched_user
            purchaser.save()


def bpt_save_order_to_database(event_id, bpt_order):
    '''
    Function takes an XML order object from the BPT order list call and
    returns an equivalent transaction object.

    event_id - the ID of the event associated to this order
    bpt_order - the order object from the BPT call
    Returns:  the Transaction object.  May throw an exception.
    '''
    trans = Transaction()

    # Locate the TicketItem or throw exception if it doesn't exist.

    ticket_item_id = '%s-%s' % (event_id, bpt_order.find('price_id').text)
    if not TicketItem.objects.filter(ticket_id=ticket_item_id).exists():
        logger.error("Ticket Item for id %s does not exist" % (
            ticket_item_id))
        return False
    trans.ticket_item = TicketItem.objects.get(ticket_id=ticket_item_id)

    trans.amount = trans.ticket_item.cost

    # Build a purchaser object.

    purchaser = Purchaser()
    purchaser.first_name = str(bpt_order.find('fname').text)
    purchaser.last_name = str(bpt_order.find('lname').text)
    purchaser.address = str(bpt_order.find('address').text)
    purchaser.city = str(bpt_order.find('city').text)
    purchaser.state = str(bpt_order.find('state').text)
    purchaser.zip = str(bpt_order.find('zip').text)
    purchaser.country = str(bpt_order.find('country').text)
    purchaser.email = str(bpt_order.find('email').text)
    purchaser.phone = str(bpt_order.find('phone').text)

    # This is a little bit of a hack.. if we don't know who the user is that
    # purchased the ticket, we assign it to the limbo user.

    tracker_id = str(bpt_order.find('tracker_id').text)
    matched_user = attempt_match_purchaser_to_user(purchaser, tracker_id)

    if matched_user is None:
        purchaser.matched_to_user = User.objects.get(username='limbo')
    else:
        purchaser.matched_to_user = matched_user

    # Attempt to see if purchaser exists in database, otherwise it is new.

    pur_id = locate_matching_purchaser(purchaser)
    if (pur_id != -1):
        trans.purchaser = Purchaser.objects.get(id=pur_id)
    else:
        purchaser.save()
        pur_id = locate_matching_purchaser(purchaser)
        trans.purchaser = Purchaser.objects.get(id=pur_id)

    # Build out the remainder of the transaction.

    trans.order_date = pytz.utc.localize(
        datetime.strptime(
            bpt_order.find('order_time').text,
            "%Y-%m-%d %H:%M:%S"))
    trans.shipping_method = str(bpt_order.find('shipping_method').text)
    trans.order_notes = str(bpt_order.find('order_notes').text)
    trans.reference = str(bpt_order.find('ticket_number').text)
    trans.payment_source = 'Brown Paper Tickets'

    trans.save()
    return True


def attempt_match_purchaser_to_user(purchaser, tracker_id=None):
    '''
    Function attempts to match a given purchaser to a user in the system, using
    the algorithm agreed upon by Betty and Scratch.

    purchaser - the purchaser object to attempt match with
    tracker_id - the tracker ID returned from Brown paper tickets
    returns:  a user id (as an integer) that matched, or -1 if none
    '''

    # First try to match the tracker id to a user in the system
    if tracker_id is not None and isinstance(tracker_id, int):
        user_id = int(tracker_id[3:])
        return User.objects.get(id=user_id)

    # Next try to match to a purchase email address from the Profile
    # (Manual Override Mechanism)

    for profile in Profile.objects.filter(
            purchase_email__iexact=purchaser.email):
        return profile.user_object

    # Finally, try to match to the user's email.  If an overriding
    # purchase_email from the Profile exists for a given user, ignore
    # the user email field for that user.

    for user in User.objects.filter(email__iexact=purchaser.email):
        if not hasattr(
                user,
                'profile') or user.profile.purchase_email is None or len(
                user.profile.purchase_email) == 0:
            return user
    return None


def locate_matching_purchaser(other_pur):
    '''
    Function returns a purchaser object ID if the given purchaser is equivalent
    to one found in the database.  Otherwise returns -1

    other_p - the purchaser to use for comparison.
    returns - the ID if it exists, otherwise -1
    '''
    for pur in Purchaser.objects.all():
        if (pur == other_pur):
            return pur.id
    return -1


def transaction_reference_exists(ref_id):
    '''
    Function checks to see if a transaction with the given reference ID exists
    in the database.  If so, we don't want to duplicat the information.

    ref_id - the reference id to check.
    returns - true if it exists, false if not.
    '''
    return (Transaction.objects.filter(reference=ref_id).exists())
