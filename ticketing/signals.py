from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from ticketing.models import (
    PayPalSettings,
    Purchaser,
    Transaction,
)
from django.contrib.auth.models import User
from django.db.models import Sum
from gbe.models import (
    Act,
    Vendor,
)
from ticketing.functions import get_fee_list
from gbe.email.functions import (
    notify_admin_on_error,
    notify_reviewers_on_bid_change,
)
from django.core.urlresolvers import reverse


@receiver(valid_ipn_received)
def pay_application_fee(sender, **kwargs):
    activity = "PayPal Purchase Processing"
    ipn_obj = sender
    ipn_obj_link = reverse("admin:%s_%s_change" % (
        "ipn",
        "paypalipn"), args=(ipn_obj.id,))
    paid = False
    purchased_tickets = []
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # Check that the receiver email has not been tampered with
        if ipn_obj.receiver_email != PayPalSettings.objects.first(
                ).business_email:
            # Not a valid payment
            notify_admin_on_error(
                activity,
                "Email not valid: %s" % ipn_obj.receiver_email,
                ipn_obj_link)
            return

        # Get user and bid
        custom = ipn_obj.custom.split('-')
        if custom[0] not in ('Act', 'Vendor') or custom[2] != "User":
            notify_admin_on_error(
                activity,
                "Can't parse custom: %s" % ipn_obj.custom,
                ipn_obj_link)
            return
        try:
            user = User.objects.get(pk=int(custom[3]))
            bid = eval(custom[0]).objects.get(pk=int(custom[1]))
        except:
            notify_admin_on_error(
                activity,
                "Can't get object in custom: %s" % ipn_obj.custom,
                ipn_obj_link)
            return

        # Check values
        ticket_items = get_fee_list(custom[0], bid.b_conference)
        ticket_pk_list = list(map(int, ipn_obj.item_number.split()))

        # minimum should be more than suggested donation
        if ticket_items.filter(is_minimum=True).exists() and float(
                ipn_obj.mc_gross) >= ticket_items.filter(
                is_minimum=True).order_by('cost').first().cost and (
                ipn_obj.mc_currency == 'USD'):
            paid = True
            purchased_tickets = [ticket_items.filter(
                is_minimum=True).order_by('cost').first()]
        # or total set of items should match total cost, and there should be
        # one non-add-on
        elif len(ticket_pk_list) > 0:
            counter = 1
            total = 0
            cost = ticket_items.filter(id__in=ticket_pk_list).aggregate(
                Sum('cost'))
            if float(ipn_obj.mc_gross) >= float(cost['cost__sum']) and (
                    ipn_obj.mc_currency == 'USD') and ticket_items.filter(
                    id__in=ticket_pk_list, add_on=False).exists():
                paid = True
                purchased_tickets = ticket_items.filter(pk__in=ticket_pk_list)
            elif not ticket_items.filter(
                    id__in=ticket_pk_list, add_on=False).exists():
                notify_admin_on_error(
                    activity,
                    "Add ons received without a main ticket",
                    ipn_obj_link)
                return
        if paid:
            buyer = Purchaser(matched_to_user=user,
                              first_name=ipn_obj.first_name,
                              last_name=ipn_obj.last_name,
                              address=ipn_obj.address_street,
                              city=ipn_obj.address_city,
                              state=ipn_obj.address_state,
                              zip=ipn_obj.address_zip,
                              country=ipn_obj.address_country,
                              email=ipn_obj.payer_email,
                              phone=ipn_obj.contact_phone)
            buyer.save()
            for ticket in purchased_tickets:
                amount = ticket.cost
                if ticket.is_minimum is True:
                    amount = ipn_obj.mc_gross
                transaction = Transaction(
                    ticket_item=ticket,
                    purchaser=buyer,
                    amount=amount,
                    order_date=ipn_obj.payment_date,
                    payment_source="PayPalIPN",
                    invoice=ipn_obj.invoice,
                    custom=ipn_obj.custom)
                transaction.save()
            bid.submitted = True
            bid.save()
            notify_reviewers_on_bid_change(
                user.profile,
                bid,
                bid.__class__.__name__,
                "Submission",
                bid.b_conference,
                '%s Reviewers' % bid.__class__.__name__,
                reverse('%s_review' % bid.__class__.__name__.lower(),
                        urlconf='gbe.urls'))
        else:
            notify_admin_on_error(
                activity,
                "Transaction was not paid",
                ipn_obj_link)
