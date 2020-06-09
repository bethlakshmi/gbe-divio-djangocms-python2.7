from django.test import TestCase
from paypal.standard.ipn.tests.test_ipn import (
    IPN_POST_PARAMS,
    IPNUtilsMixin,
    MockedPostbackMixin,
)
from paypal.standard.ipn.signals import valid_ipn_received
from ticketing.signals import pay_application_fee
from django.test.utils import override_settings
from tests.functions.ticketing_functions import setup_fees
from tests.factories.gbe_factories import (
    ActFactory,
    ProfileFactory,
    VendorFactory,
)
from ticketing.models import (
    PayPalSettings,
    Purchaser,
    Transaction,
)
from paypal.standard.ipn.models import PayPalIPN
from tests.functions.gbe_functions import (
    assert_right_mail_right_addresses,
    grant_privilege,
)
from django.conf import settings
from django.core.urlresolvers import reverse


@override_settings(ROOT_URLCONF='paypal.standard.ipn.tests.test_urls')
class TestSignals(MockedPostbackMixin, IPNUtilsMixin, TestCase):
    # See https://github.com/spookylukey/django-paypal/blob/master/ ...
    # ... paypal/standard/ipn/tests/test_ipn.py
    # For source material inherited here.
    def assertGotSignal(self, signal, params=IPN_POST_PARAMS):
        signal.connect(pay_application_fee)
        response = self.paypal_post(params)
        self.assertEqual(response.status_code, 200)
        ipns = PayPalIPN.objects.all()
        self.assertEqual(len(ipns), 1)
        ipn_obj = ipns[0]
        self.assertEqual(ipn_obj.flag, False)
        return ipn_obj

    def test_valid_act_payment_received(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Act Reviewers')
        act = ActFactory()
        tickets = setup_fees(act.b_conference, is_act=True)
        act_params = IPN_POST_PARAMS
        act_params["mc_currency"] = "USD"
        act_params["receiver_email"] = PayPalSettings.objects.first(
            ).business_email
        act_params["custom"] = "%s-%d-User-%d" % (
            "Act",
            act.pk,
            act.performer.contact.user_object.pk)
        act_params["mc_gross"] = 10.00
        ipn_obj = self.assertGotSignal(valid_ipn_received,
                                       params=act_params)
        purchaser = Purchaser.objects.get(
            matched_to_user=act.performer.contact.user_object)
        transaction = Transaction.objects.get(purchaser=purchaser)
        self.assertEqual(transaction.ticket_item, tickets[0])
        self.assertEqual(transaction.invoice, ipn_obj.invoice)
        self.assertEqual(purchaser.first_name, ipn_obj.first_name)
        assert_right_mail_right_addresses(
            0,
            1,
            "Act Submission Occurred",
            [privileged_profile.contact_email])

    def test_valid_vendor_payment_received(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Vendor Reviewers')
        vendor = VendorFactory()
        tickets = setup_fees(vendor.b_conference, is_vendor=True)
        vendor_params = IPN_POST_PARAMS
        vendor_params["receiver_email"] = PayPalSettings.objects.first(
            ).business_email
        vendor_params["custom"] = "%s-%d-User-%d" % (
            "Vendor",
            vendor.pk,
            vendor.profile.user_object.pk)
        cost = 0
        for ticket in tickets:
            cost = cost + ticket.cost
        vendor_params["mc_currency"] = "USD"
        vendor_params["mc_gross"] = cost
        vendor_params["item_number"] = "%d %d" % (tickets[0].pk, tickets[1].pk)
        ipn_obj = self.assertGotSignal(valid_ipn_received,
                                       params=vendor_params)
        self.assertTrue(Purchaser.objects.filter(
            matched_to_user=vendor.profile.user_object).exists())
        purchaser = Purchaser.objects.get(
            matched_to_user=vendor.profile.user_object)
        self.assertEqual(purchaser.first_name, ipn_obj.first_name)
        transactions = Transaction.objects.filter(purchaser=purchaser)
        for ticket in tickets:
            self.assertTrue(transactions.filter(ticket_item=ticket).exists())
            self.assertEqual(
                transactions.filter(ticket_item=ticket).first().invoice,
                ipn_obj.invoice)
        assert_right_mail_right_addresses(
            0,
            1,
            "Vendor Submission Occurred",
            [privileged_profile.contact_email])

    def test_bad_reciever(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Act Reviewers')
        act = ActFactory()
        tickets = setup_fees(act.b_conference, is_act=True)
        act_params = IPN_POST_PARAMS
        act_params["mc_currency"] = "USD"
        act_params["receiver_email"] = "bad@email.com"

        ipn_obj = self.assertGotSignal(valid_ipn_received,
                                       params=act_params)
        msg = assert_right_mail_right_addresses(
            0,
            1,
            "PayPal Purchase Processing Error",
            [admin[1] for admin in settings.ADMINS])
        self.assertTrue(
            "Email not valid: %s" % ipn_obj.receiver_email in msg.body)
        self.assertTrue(reverse("admin:%s_%s_change" % (
            "ipn",
            "paypalipn"), args=(ipn_obj.id, )) in msg.body)

    def test_bad_bid_type(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Act Reviewers')
        act = ActFactory()
        tickets = setup_fees(act.b_conference, is_act=True)
        act_params = IPN_POST_PARAMS
        act_params["mc_currency"] = "USD"
        act_params["receiver_email"] = PayPalSettings.objects.first(
            ).business_email
        act_params["custom"] = "%s-%d-User-%d" % (
            "BadBidType",
            act.pk,
            act.performer.contact.user_object.pk)
        ipn_obj = self.assertGotSignal(valid_ipn_received,
                                       params=act_params)
        msg = assert_right_mail_right_addresses(
            0,
            1,
            "PayPal Purchase Processing Error",
            [admin[1] for admin in settings.ADMINS])
        self.assertTrue(
            "Can't parse custom: %s" % ipn_obj.custom in msg.body)
        self.assertTrue(reverse("admin:%s_%s_change" % (
            "ipn",
            "paypalipn"), args=(ipn_obj.id, )) in msg.body)

    def test_bad_bid_id(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Act Reviewers')
        act = ActFactory()
        tickets = setup_fees(act.b_conference, is_act=True)
        act_params = IPN_POST_PARAMS
        act_params["mc_currency"] = "USD"
        act_params["receiver_email"] = PayPalSettings.objects.first(
            ).business_email
        act_params["custom"] = "%s-%d-User-%d" % (
            "Act",
            act.pk,
            act.performer.contact.user_object.pk+100)
        ipn_obj = self.assertGotSignal(valid_ipn_received,
                                       params=act_params)
        msg = assert_right_mail_right_addresses(
            0,
            1,
            "PayPal Purchase Processing Error",
            [admin[1] for admin in settings.ADMINS])
        self.assertTrue(
            "Can't get object in custom: %s" % ipn_obj.custom in msg.body)
        self.assertTrue(reverse("admin:%s_%s_change" % (
            "ipn",
            "paypalipn"), args=(ipn_obj.id, )) in msg.body)

    def test_low_donation(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Act Reviewers')
        act = ActFactory()
        tickets = setup_fees(act.b_conference, is_act=True)
        act_params = IPN_POST_PARAMS
        act_params["mc_currency"] = "USD"
        act_params["receiver_email"] = PayPalSettings.objects.first(
            ).business_email
        act_params["custom"] = "%s-%d-User-%d" % (
            "Act",
            act.pk,
            act.performer.contact.user_object.pk)
        act_params["mc_gross"] = "5.00"
        ipn_obj = self.assertGotSignal(valid_ipn_received,
                                       params=act_params)
        msg = assert_right_mail_right_addresses(
            0,
            1,
            "PayPal Purchase Processing Error",
            [admin[1] for admin in settings.ADMINS])
        self.assertTrue("Transaction was not paid" in msg.body)
        self.assertTrue(reverse("admin:%s_%s_change" % (
            "ipn",
            "paypalipn"), args=(ipn_obj.id, )) in msg.body)

    def test_low_ticket_payment(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Vendor Reviewers')
        vendor = VendorFactory()
        tickets = setup_fees(vendor.b_conference, is_vendor=True)
        vendor_params = IPN_POST_PARAMS
        vendor_params["receiver_email"] = PayPalSettings.objects.first(
            ).business_email
        vendor_params["custom"] = "%s-%d-User-%d" % (
            "Vendor",
            vendor.pk,
            vendor.profile.user_object.pk)
        cost = 0
        for ticket in tickets:
            cost = cost + ticket.cost
        vendor_params["mc_currency"] = "USD"
        vendor_params["mc_gross"] = cost - 10.00
        vendor_params["item_number"] = "%d %d" % (tickets[0].pk, tickets[1].pk)
        ipn_obj = self.assertGotSignal(valid_ipn_received,
                                       params=vendor_params)
        msg = assert_right_mail_right_addresses(
            0,
            1,
            "PayPal Purchase Processing Error",
            [admin[1] for admin in settings.ADMINS])
        self.assertTrue("Transaction was not paid" in msg.body)
        self.assertTrue(reverse("admin:%s_%s_change" % (
            "ipn",
            "paypalipn"), args=(ipn_obj.id, )) in msg.body)

    def test_wrong_currency_payment(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Vendor Reviewers')
        vendor = VendorFactory()
        tickets = setup_fees(vendor.b_conference, is_vendor=True)
        vendor_params = IPN_POST_PARAMS
        vendor_params["receiver_email"] = PayPalSettings.objects.first(
            ).business_email
        vendor_params["custom"] = "%s-%d-User-%d" % (
            "Vendor",
            vendor.pk,
            vendor.profile.user_object.pk)
        cost = 0
        for ticket in tickets:
            cost = cost + ticket.cost
        vendor_params["mc_currency"] = "EUR"
        vendor_params["mc_gross"] = cost
        vendor_params["item_number"] = "%d %d" % (tickets[0].pk, tickets[1].pk)
        ipn_obj = self.assertGotSignal(valid_ipn_received,
                                       params=vendor_params)
        msg = assert_right_mail_right_addresses(
            0,
            1,
            "PayPal Purchase Processing Error",
            [admin[1] for admin in settings.ADMINS])
        self.assertTrue("Transaction was not paid" in msg.body)
        self.assertTrue(reverse("admin:%s_%s_change" % (
            "ipn",
            "paypalipn"), args=(ipn_obj.id, )) in msg.body)

    def test_no_main_ticket(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Vendor Reviewers')
        vendor = VendorFactory()
        tickets = setup_fees(vendor.b_conference, is_vendor=True)
        vendor_params = IPN_POST_PARAMS
        vendor_params["receiver_email"] = PayPalSettings.objects.first(
            ).business_email
        vendor_params["custom"] = "%s-%d-User-%d" % (
            "Vendor",
            vendor.pk,
            vendor.profile.user_object.pk)
        cost = 0
        for ticket in tickets:
            cost = cost + ticket.cost
        vendor_params["mc_currency"] = "USD"
        vendor_params["mc_gross"] = cost
        vendor_params["item_number"] = str(tickets[1].pk)
        ipn_obj = self.assertGotSignal(valid_ipn_received,
                                       params=vendor_params)
        msg = assert_right_mail_right_addresses(
            0,
            1,
            "PayPal Purchase Processing Error",
            [admin[1] for admin in settings.ADMINS])
        self.assertTrue("Add ons received without a main ticket" in msg.body)
        self.assertTrue(reverse("admin:%s_%s_change" % (
            "ipn",
            "paypalipn"), args=(ipn_obj.id, )) in msg.body)

    def test_valid_vendor_payment_already_submitted(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Vendor Reviewers')
        vendor = VendorFactory(submitted=True)
        tickets = setup_fees(vendor.b_conference, is_vendor=True)
        vendor_params = IPN_POST_PARAMS
        vendor_params["receiver_email"] = PayPalSettings.objects.first(
            ).business_email
        vendor_params["custom"] = "%s-%d-User-%d" % (
            "Vendor",
            vendor.pk,
            vendor.profile.user_object.pk)
        cost = 0
        for ticket in tickets:
            cost = cost + ticket.cost
        vendor_params["mc_currency"] = "USD"
        vendor_params["mc_gross"] = cost
        vendor_params["item_number"] = str(tickets[0].pk)
        ipn_obj = self.assertGotSignal(valid_ipn_received,
                                       params=vendor_params)
        self.assertEqual(Purchaser.objects.filter(
            matched_to_user=vendor.profile.user_object).count(), 1)
        self.assertEqual(Transaction.objects.filter(
            purchaser__matched_to_user=vendor.profile.user_object).count(), 1)
        msg = assert_right_mail_right_addresses(
            0,
            2,
            "PayPal Purchase Processing Error",
            [admin[1] for admin in settings.ADMINS])
        self.assertTrue(
            "Payment recieved for a bid that has already been " +
            "submitted.  Bid name: %s, Bid Type: %s, Bid PK: %s" % (
                vendor.b_title,
                "Vendor",
                vendor.pk))
        self.assertTrue(reverse("admin:%s_%s_change" % (
            "ipn",
            "paypalipn"), args=(ipn_obj.id, )) in msg.body)
