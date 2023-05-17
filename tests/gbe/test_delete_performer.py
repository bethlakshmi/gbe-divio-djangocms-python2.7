from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ActFactory,
    BioFactory,
    ClassFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
)
from gbetext import delete_in_use


class TestDeletePerformer(TestCase):
    view_name = 'performer-delete'

    '''Tests for edit_persona view'''
    def setUp(self):
        self.client = Client()
        self.persona = BioFactory()
        self.url = reverse(self.view_name,
                           urlconf="gbe.urls",
                           args=[self.persona.pk])

    def test_wrong_profile(self):
        viewer = ProfileFactory()
        login_as(viewer, self)
        response = self.client.post(self.url, data={'submit': 'Confirm'})
        self.assertEqual(response.status_code, 404)

    def test_delete_performer_has_message(self):
        login_as(self.persona.contact, self)
        response = self.client.post(self.url,
                                    data={'submit': 'Confirm'},
                                    follow=True)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))
        assert_alert_exists(
            response,
            'success',
            'Success',
            "Successfully deleted persona %s" % str(self.persona))

    def test_delete_performer_with_bid(self):
        ClassFactory(teacher=self.persona)
        login_as(self.persona.contact, self)
        response = self.client.post(self.url,
                                    data={'submit': 'Confirm'},
                                    follow=True)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))
        assert_alert_exists(
            response,
            'danger',
            'Error',
            delete_in_use)

    def test_delete_troupe(self):
        self.troupe = BioFactory(multiple_performers=True)
        self.url = reverse(self.view_name,
                           urlconf="gbe.urls",
                           args=[self.troupe.pk])
        login_as(self.troupe.contact, self)
        response = self.client.post(self.url,
                                    data={'submit': 'Confirm'},
                                    follow=True)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))
        assert_alert_exists(
            response,
            'success',
            'Success',
            "Successfully deleted persona %s" % str(self.troupe))

    def test_delete_troupe_with_bid(self):
        self.troupe = BioFactory(multiple_performers=True)
        self.url = reverse(self.view_name,
                           urlconf="gbe.urls",
                           args=[self.troupe.pk])
        ActFactory(performer=self.troupe)
        login_as(self.troupe.contact, self)
        response = self.client.post(self.url,
                                    data={'submit': 'Confirm'},
                                    follow=True)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))
        assert_alert_exists(
            response,
            'danger',
            'Error',
            delete_in_use)

