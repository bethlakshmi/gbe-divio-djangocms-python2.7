from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    TroupeFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe.functions import validate_profile


class TestLimitedPerformerAutoComplete(TestCase):
    url = reverse('coordinator-performer-autocomplete', urlconf="gbe.urls")

    def setUp(self):
        self.client = Client()
        self.privileged_user = ProfileFactory.create().user_object
        grant_privilege(self.privileged_user,
                        'Act Coordinator',
                        'view_performer')
        login_as(self.privileged_user, self)
        self.persona = PersonaFactory()
        self.troupe = TroupeFactory()

    def test_list_performer(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.persona.name)
        self.assertContains(response, self.persona.pk)
        self.assertContains(response, self.troupe.name)
        self.assertContains(response, self.troupe.pk)

    def test_list_personae_w_search_by_persona_name(self):
        response = self.client.get("%s?q=%s" % (self.url, self.persona.name))
        self.assertContains(response, self.persona.name)
        self.assertContains(response, self.persona.pk)
        self.assertNotContains(response, self.troupe.name)
