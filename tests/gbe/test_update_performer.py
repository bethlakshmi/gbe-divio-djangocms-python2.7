from django.test import TestCase
from django.urls import reverse
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    PersonaFactory,
    TroupeFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
)


class TestUpdatePerformer(TestCase):
    '''Tests for edit_troupe view'''

    view_name = 'performer-update'

    def setUp(self):
        self.client = Client()

    def test_update_persona(self):
        '''edit_troupe view, create flow
        '''
        contact = PersonaFactory()
        login_as(contact.performer_profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[contact.pk])
        response = self.client.get(url + "?_popup=1", follow=True)
        self.assertRedirects(
            response,
            "%s?_popup=1" % reverse(
                'persona-update',
                urlconf="gbe.urls",
                args=[contact.pk, 1]))

    def test_update_troupe(self):
        troupe = TroupeFactory()
        login_as(troupe.contact, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[troupe.pk])
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('troupe-update', urlconf="gbe.urls", args=[troupe.pk]))

    def test_bad_performer(self):
        troupe = TroupeFactory()
        login_as(troupe.contact, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[troupe.pk + 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
