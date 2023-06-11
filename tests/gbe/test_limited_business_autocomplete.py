from django.test import TestCase
from django.urls import reverse
from tests.factories.gbe_factories import (
    BusinessFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import login_as
from gbe.functions import validate_profile


class TestLimitedBusinessAutoComplete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('limited-business-autocomplete', urlconf='gbe.urls')
        cls.business = BusinessFactory()

    def test_list_business(self):
        profile = self.business.owners.all().first()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.business.name)
        self.assertContains(response, self.business.pk)

    def test_no_access_business(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, self.business.name)
        self.assertNotContains(response, self.business.pk)

    def test_not_users_business(self):
        user = ProfileFactory()
        login_as(user, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, self.business.name)
        self.assertNotContains(response, self.business.pk)

    def test_list_w_search_by_name(self):
        business2 = BusinessFactory(
            name="Totally different name",
            owners=[self.business.owners.all().first()])

        profile = self.business.owners.all().first()
        login_as(profile, self)
        response = self.client.get("%s?q=%s" % (self.url, self.business.name))
        self.assertContains(response, self.business.name)
        self.assertContains(response, self.business.pk)
        self.assertNotContains(response, business2.name)
