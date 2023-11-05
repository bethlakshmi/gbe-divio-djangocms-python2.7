from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ClassLabelFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import login_as
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestClassLabelAutoComplete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = ProfileFactory()
        grant_privilege(cls.user, 'Class Coordinator')

        cls.label1 = ClassLabelFactory()
        cls.label2 = ClassLabelFactory()
        cls.url = reverse('classlabel-autocomplete', urlconf="gbe.urls")

    def setUp(self):
        self.client = Client()

    def test_list(self):
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.label1.text)
        self.assertContains(response, self.label1.pk)

    def test_no_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_list_w_search(self):
        login_as(self.user, self)
        response = self.client.get("%s?q=%s" % (self.url, self.label1.text))
        self.assertContains(response, self.label1.text)
        self.assertContains(response, self.label1.pk)
        self.assertNotContains(response, self.label2.text)
