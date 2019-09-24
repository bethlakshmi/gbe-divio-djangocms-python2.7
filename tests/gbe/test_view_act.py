import nose.tools as nt
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
)
from tests.functions.gbe_functions import login_as


class TestViewAct(TestCase):
    '''Tests for view_act view'''
    view_name = 'act_view'

    def setUp(self):
        self.client = Client()

    def test_view_act_all_well(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')
        login_as(act.performer.performer_profile, self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)

    def test_edit_bid_w_redirect(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory()
        url = reverse("summer_act_view",
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(act.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse(self.view_name, args=[act.pk], urlconf="gbe.urls"))
