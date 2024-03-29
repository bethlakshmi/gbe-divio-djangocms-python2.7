from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import login_as
from gbe.functions import validate_profile


class TestLimitedPersonaAutoComplete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('limited-persona-autocomplete', urlconf='gbe.urls')

    def setUp(self):
        self.client = Client()

    def test_list_persona(self):
        persona = BioFactory()
        login_as(persona.contact.user_object, self)
        response = self.client.get(self.url)
        self.assertContains(response, persona.name)
        self.assertContains(response, persona.pk)

    def test_no_access_personae(self):
        persona = BioFactory()
        response = self.client.get(self.url)
        self.assertNotContains(response, persona.name)
        self.assertNotContains(response, persona.pk)

    def test_not_users_personae(self):
        persona = BioFactory()
        user = ProfileFactory()
        login_as(user, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, persona.name)
        self.assertNotContains(response, persona.pk)

    def test_list_personae_w_search_by_persona_name(self):
        persona1 = BioFactory()
        persona2 = BioFactory(contact=persona1.contact)
        login_as(persona1.contact.user_object, self)
        response = self.client.get("%s?q=%s" % (self.url, persona1.name))
        self.assertContains(response, persona1.name)
        self.assertContains(response, persona1.pk)
        self.assertNotContains(response, persona2.name)
