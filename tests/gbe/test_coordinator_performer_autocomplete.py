from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe.functions import validate_profile


class TestCoordinatorPerformerAutoComplete(TestCase):

    def setUp(self):
        self.client = Client()
        login_as(self.privileged_user, self)

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = ProfileFactory.create().user_object
        grant_privilege(cls.privileged_user,
                        'Act Coordinator',
                        'view_bio')
        cls.persona = BioFactory()
        cls.troupe = BioFactory(multiple_performers=True)

    def test_list_performer(self):
        url = reverse('coordinator-performer-autocomplete', urlconf="gbe.urls")
        response = self.client.get(url)
        self.assertContains(response, self.persona.name)
        self.assertContains(response, self.persona.pk)
        self.assertContains(response, self.troupe.name)
        self.assertContains(response, self.troupe.pk)

    def test_list_personae_w_search_by_persona_name(self):
        url = reverse('coordinator-performer-autocomplete', urlconf="gbe.urls")
        response = self.client.get("%s?q=%s" % (url, self.persona.name))
        self.assertContains(response, self.persona.name)
        self.assertContains(response, self.persona.pk)
        self.assertNotContains(response, self.troupe.name)
