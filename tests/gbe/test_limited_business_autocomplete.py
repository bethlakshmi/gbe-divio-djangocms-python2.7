from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    BusinessFactory,
    ProfileFactory,
    TroupeFactory,
)
from tests.functions.gbe_functions import login_as
from gbe.functions import validate_profile


class TestLimitedBusinessAutoComplete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('limited-business-autocomplete', urlconf='gbe.urls')

    def setUp(self):
        self.client = Client()

    def test_list_business(self):
        business = BusinessFactory()
        profile = business.owners.all().first()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, business.name)
        self.assertContains(response, business.pk)

    def test_no_access_business(self):
        business = BusinessFactory()
        response = self.client.get(self.url)
        self.assertNotContains(response, business.name)
        self.assertNotContains(response, business.pk)

    def test_not_users_business(self):
        business = BusinessFactory()
        user = ProfileFactory()
        login_as(user, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, business.name)
        self.assertNotContains(response, business.pk)

    def test_list_w_search_by_name(self):
        business = BusinessFactory()
        business2 = BusinessFactory(
            name="Totally different name",
            owners=[business.owners.all().first()])

        profile = business.owners.all().first()
        login_as(profile, self)
        response = self.client.get("%s?q=%s" % (self.url, business.name))
        self.assertContains(response, business.name)
        self.assertContains(response, business.pk)
        self.assertNotContains(response, business2.name)
