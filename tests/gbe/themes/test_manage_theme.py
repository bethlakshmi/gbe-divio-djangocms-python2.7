from django.test import TestCase
from django.test import Client
from django.urls import reverse
from inventory.tests.factories import (
    StyleValueFactory,
    StyleVersionFactory,
    UserFactory
)
from inventory.tests.functions import (
    login_as,
    assert_option_state,
)
from datetime import (
    date,
    timedelta,
)
from inventory.models import Item


class TestManageTheme(TestCase):
    view_name = "manage_theme"

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.value = StyleValueFactory()
        self.url = reverse(
            self.view_name,
            urlconf="inventory.urls",
            args=[self.value.style_version.pk])
        self.title = "Manage Styles Settings for %s, version %d" % (
            self.value.style_version.name,
            self.value.style_version.number)
        self.style_url = reverse(
            "theme_style",
            urlconf="inventory.urls",
            args=[self.value.style_version.pk])

    def test_no_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             "/login/?next=%s" % self.url,
                             fetch_redirect_response=False)

    def test_get(self):
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.title)
        self.assertContains(response, self.value.value)
        self.assertContains(response,
                            self.value.style_property.selector)
        self.assertContains(response,
                            self.value.style_property.selector.used_for)
        self.assertContains(response,
                            self.value.style_property.style_property)
        self.assertContains(response, self.style_url)

    def test_get_empty(self):
        empty = StyleVersionFactory()
        login_as(self.user, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="inventory.urls",
            args=[empty.pk]))
        self.assertContains(
            response,
            "Manage Styles Settings for %s, version %d" % (
                empty.name,
                empty.number))
        self.assertContains(response, reverse(
            "theme_style",
            urlconf="inventory.urls",
            args=[empty.pk]))

    def test_get_bad_id(self):
        login_as(self.user, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="inventory.urls",
            args=[self.value.style_version.pk+1]))
        self.assertEqual(404, response.status_code)

    def test_post_basics_finish(self):
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            '%s-value' % self.value.pk: "rgba(255, 255, 255, 0)",
            'finish': "Finish",
            }, follow=True)
        self.assertContains(
            response,
            "Updated %s" % self.value.style_version)
        self.assertRedirects(response,
                             reverse("items_list", urlconf="inventory.urls"))

    def test_post_basics_update(self):
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            '%s-value' % self.value.pk: "rgba(255, 255, 255, 0)",
            'update': "Update",
            }, follow=True)
        self.assertContains(response, self.title)
        self.assertContains(
            response,
            "Updated %s" % self.value.style_version)
        self.assertContains(response, 'rgba(255, 255, 255, 0)')
        self.assertContains(response,
                            self.value.style_property.selector)
        self.assertContains(response,
                            self.value.style_property.selector.used_for)
        self.assertContains(response,
                            self.value.style_property.style_property)
        self.assertContains(response, self.style_url)

    def test_cancel(self):
        login_as(self.user, self)
        response = self.client.post(
            self.url,
            data={'cancel': "Cancel"},
            follow=True)
        self.assertContains(response, "The last update was canceled.")
        self.assertRedirects(response,
                             reverse("items_list", urlconf="inventory.urls"))

    def test_post_basics_bad_data(self):
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            'finish': "Finish",
            }, follow=True)
        self.assertContains(response, self.title)
        self.assertContains(response, "There is an error on the form.")
        self.assertContains(response, self.style_url)
