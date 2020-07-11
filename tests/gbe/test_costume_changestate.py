import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    CostumeFactory,
    ProfileFactory
)
from django.core.exceptions import PermissionDenied
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestCostumeChangestate(TestCase):
    '''Tests for costume_changestate view'''
    view_name = 'costume_changestate'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.costume = CostumeFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Costume Coordinator')
        self.data = {'accepted': '3'}

    def test_costume_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        url = reverse(self.view_name,
                      args=[self.costume.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        nt.assert_equal(response.status_code, 302)

    def test_costume_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        url = reverse(self.view_name,
                      args=[self.costume.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.post(url, data=self.data)
        nt.assert_equal(response.status_code, 403)
