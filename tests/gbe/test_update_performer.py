from django.test import TestCase
from django.urls import reverse
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import BioFactory
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
)
from tests.functions.scheduler_functions import get_or_create_bio


class TestUpdatePerformer(TestCase):
    '''Tests for edit_troupe view'''

    view_name = 'performer-update'

    def setUp(self):
        self.client = Client()

    def test_update_persona(self):
        '''edit_troupe view, create flow
        '''
        performer = BioFactory()
        login_as(performer.contact, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[performer.pk])
        response = self.client.get(url + "?_popup=1", follow=True)
        self.assertRedirects(
            response,
            "%s?_popup=1" % reverse(
                'persona-update',
                urlconf="gbe.urls",
                args=[performer.pk]))

    def test_bad_performer(self):
        troupe = BioFactory(multiple_performers=True)
        login_as(troupe.contact, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[troupe.pk + 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
