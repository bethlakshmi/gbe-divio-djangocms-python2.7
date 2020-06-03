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
)
from ticketing.models import (
    PayPalSettings,
    Purchaser,
    Transaction,
)
from paypal.standard.ipn.models import PayPalIPN


@override_settings(ROOT_URLCONF='paypal.standard.ipn.tests.test_urls')
class TestSignals(MockedPostbackMixin, IPNUtilsMixin, TestCase):

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
        act = ActFactory()
        tickets = setup_fees(act.b_conference, is_act=True)
        act_params = IPN_POST_PARAMS
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
