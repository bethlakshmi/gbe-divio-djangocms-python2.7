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

    @classmethod
    def setUpTestData(cls):
        cls.user = ProfileFactory()
        cls.persona1 = PersonaFactory()
        cls.persona2 = PersonaFactory()
        cls.url = reverse('persona-autocomplete', urlconf="gbe.urls")

    def setUp(self):
        self.client = Client()

    def test_list_persona(self):
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.persona1.name)
        self.assertContains(response, self.persona1.pk)

    def test_no_access_personae(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, self.persona1.name)
        self.assertNotContains(response, self.persona1.pk)

    def test_list_personae_w_search_by_persona_name(self):
        login_as(self.user, self)
        response = self.client.get("%s?q=%s" % (self.url, self.persona1.name))
        self.assertContains(response, self.persona1.name)
        self.assertContains(response, self.persona1.pk)
        self.assertNotContains(response, self.persona2.name)

    def test_list_personae_w_search_by_profile_name(self):
        login_as(self.user, self)
        response = self.client.get("%s?q=%s" % (
            self.url,
            self.persona1.performer_profile.display_name))
        self.assertContains(response, self.persona1.name)
        self.assertContains(response, self.persona1.pk)
        self.assertNotContains(response, self.persona2.name)

    def test_list_personae_w_search_by_label(self):
        persona1 = PersonaFactory(label="find me")
        login_as(self.user, self)
        response = self.client.get("%s?q=%s" % (self.url, "find me"))
        self.assertContains(response, persona1.name)
        self.assertContains(response, persona1.pk)
        self.assertNotContains(response, self.persona2.name)
