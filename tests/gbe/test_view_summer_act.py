from django.urls import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
)
from tests.functions.gbe_functions import login_as


class TestViewSummerAct(TestCase):
    '''Tests for view_act view'''
    view_name = 'summeract_view'

    def setUp(self):
        self.client = Client()
        login_as(self.act.performer.contact, self)

    @classmethod
    def setUpTestData(cls):
        cls.conference = ConferenceFactory(act_style="summer")
        cls.act = ActFactory(b_conference=cls.conference)

    def test_view_act_all_well(self):
        url = reverse(self.view_name,
                      args=[self.act.pk],
                      urlconf='gbe.urls')
        response = self.client.get(url)
        test_string = 'The Summer Act'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_string)

    def test_edit_bid_w_redirect(self):
        '''edit_bid, not post, should take us to edit process'''
        url = reverse("act_view",
                      args=[self.act.pk],
                      urlconf="gbe.urls")

        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse(self.view_name, args=[self.act.pk], urlconf="gbe.urls"))
