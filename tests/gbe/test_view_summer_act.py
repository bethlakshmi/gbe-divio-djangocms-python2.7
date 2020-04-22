import nose.tools as nt
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
)
from tests.functions.gbe_functions import login_as


class TestViewSummerAct(TestCase):
    '''Tests for view_act view'''
    view_name = 'summer_act_view'

    def setUp(self):
        self.client = Client()
        self.conference = ConferenceFactory(act_style="summer")
        self.act = ActFactory(b_conference=self.conference)

    def test_view_act_all_well(self):
        url = reverse(self.view_name,
                      args=[self.act.pk],
                      urlconf='gbe.urls')
        login_as(self.act.performer.performer_profile, self)
        response = self.client.get(url)
        test_string = 'The Summer Act'
        nt.assert_equal(response.status_code, 200)
        self.assertContains(response, test_string)

    def test_edit_bid_w_redirect(self):
        '''edit_bid, not post, should take us to edit process'''
        url = reverse("act_view",
                      args=[self.act.pk],
                      urlconf="gbe.urls")

        login_as(self.act.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse(self.view_name, args=[self.act.pk], urlconf="gbe.urls"))
