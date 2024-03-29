from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import login_as
from gbe.functions import validate_profile


class TestLimitedPerformerAutoComplete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('limited-performer-autocomplete', urlconf='gbe.urls')

    def setUp(self):
        self.client = Client()

    def test_list_performer(self):
        troupe = BioFactory(multiple_performers=True)
        login_as(troupe.contact.user_object, self)
        response = self.client.get(self.url)
        self.assertContains(response, troupe.name)
        self.assertContains(response, troupe.pk)

    def test_no_access_personae(self):
        persona = BioFactory()
        response = self.client.get(self.url)
        self.assertNotContains(response, persona.name)
        self.assertNotContains(response, persona.pk)

    def test_not_users_personae(self):
        troupe = BioFactory(multiple_performers=True)
        user = ProfileFactory()
        login_as(user, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, troupe.name)
        self.assertNotContains(response, troupe.pk)

    def test_list_personae_w_search_by_persona_name(self):
        persona1 = BioFactory()
        troupe1 = BioFactory(contact=persona1.contact,
                             multiple_performers=True)
        login_as(troupe1.contact.user_object, self)
        response = self.client.get("%s?q=%s" % (self.url, troupe1.name))
        self.assertContains(response, troupe1.name)
        self.assertContains(response, troupe1.pk)
        self.assertNotContains(response, persona1.name)
