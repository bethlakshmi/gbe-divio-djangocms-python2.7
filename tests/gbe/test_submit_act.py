import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ActFactory,
    ProfileFactory,
)
from gbe.models import Act
from tests.functions.gbe_functions import login_as


class TestSubmitAct(TestCase):
    '''Tests for submit_act view'''
    view_name = 'act_submit'

    def setUp(self):
        self.client = Client()

    def test_submit_act(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')
        login_as(act.performer.performer_profile, self)
        response = self.client.get(url, follow=True)
        redirect = ('http://testserver/gbe', 302)
        nt.assert_true(redirect in response.redirect_chain)
        nt.assert_true("Profile View" in response.content)
        nt.assert_equal(response.status_code, 200)

    def test_submit_act_does_not_exist(self):
        Act.objects.all().delete()
        url = reverse(self.view_name,
                      args=[0],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(404, response.status_code)

    def test_submit_act_not_owner(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')

        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        error_string = "Error: You don&#39;t own that act."
        nt.assert_true(error_string in response.content)
