from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import login_as
from gbe.functions import validate_profile


class TestPersonaAutoComplete(TestCase):
    url = reverse('persona-autocomplete')

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory()

    def test_list_persona(self):
        persona = PersonaFactory()
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, persona.name)
        self.assertContains(response, persona.pk)

    def test_no_access_personae(self):
        persona = PersonaFactory()
        response = self.client.get(self.url)
        self.assertNotContains(response, persona.name)
        self.assertNotContains(response, persona.pk)

    def test_list_personae_w_search_by_persona_name(self):
        persona1 = PersonaFactory()
        persona2 = PersonaFactory()
        login_as(self.user, self)
        response = self.client.get("%s?q=%s" % (self.url, persona1.name))
        self.assertContains(response, persona1.name)
        self.assertContains(response, persona1.pk)
        self.assertNotContains(response, persona2.name)

    def test_list_personae_w_search_by_profile_name(self):
        persona1 = PersonaFactory()
        persona2 = PersonaFactory()
        login_as(self.user, self)
        response = self.client.get("%s?q=%s" % (
            self.url,
            persona1.performer_profile.display_name))
        self.assertContains(response, persona1.name)
        self.assertContains(response, persona1.pk)
        self.assertNotContains(response, persona2.name)
