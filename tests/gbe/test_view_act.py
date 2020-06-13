from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    make_act_app_purchase,
)
from gbetext import (
    bid_not_submitted_msg,
    bid_not_paid_msg,
    default_submit_msg,
)


class TestViewAct(TestCase):
    '''Tests for view_act view'''
    view_name = 'act_view'

    def setUp(self):
        self.client = Client()

    def test_view_act_all_well(self):
        act = ActFactory(submitted=True)
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')
        login_as(act.performer.performer_profile, self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_string)
        self.assertContains(response, default_submit_msg)

    def test_edit_bid_w_redirect(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory(submitted=True)
        url = reverse("summeract_view",
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(act.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse(self.view_name, args=[act.pk], urlconf="gbe.urls"))

    def test_view_act_not_paid(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')
        login_as(act.performer.performer_profile, self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_string)
        self.assertContains(response, bid_not_paid_msg)

    def test_view_act_not_submitted(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')
        make_act_app_purchase(act.b_conference,
                              act.performer.performer_profile.user_object)
        login_as(act.performer.performer_profile, self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_string)
        self.assertContains(response, bid_not_submitted_msg)
