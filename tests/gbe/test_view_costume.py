import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import CostumeFactory
from tests.functions.gbe_functions import login_as


class TestViewCostume(TestCase):
    view_name = "costume_view"

    '''Tests for view_costume view'''
    def setUp(self):
        self.client = Client()

    def test_view_costume(self):
        '''view_costume view, success
        '''
        costume = CostumeFactory()
        url = reverse(self.view_name, urlconf="gbe.urls", args=[costume.pk])
        login_as(costume.profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
