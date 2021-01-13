from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    StyleValueFactory,
    StyleVersionFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from datetime import (
    date,
    timedelta,
)


class TestManageTheme(TestCase):
    view_name = "manage_theme"

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory().user_object
        grant_privilege(self.user, u'Theme Editor')

        self.value = StyleValueFactory()
        self.url = reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk])
        self.title = "Manage {}, version {:.1f}".format(
            self.value.style_version.name,
            self.value.style_version.number)
        self.style_url = reverse(
            "theme_style",
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk])

    def test_no_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             "/login/?next=%s" % self.url,
                             fetch_redirect_response=False)

    def test_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_get(self):
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, reverse(
            "clone_theme",
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk]))
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
            urlconf="gbe.themes.urls",
            args=[empty.pk]))
        self.assertContains(
            response,
            "Manage {}, version {:.1f}".format(empty.name, empty.number))
        self.assertContains(response, reverse(
            "theme_style",
            urlconf="gbe.themes.urls",
            args=[empty.pk]))

    def test_get_bad_id(self):
        login_as(self.user, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk+1]))
        self.assertEqual(404, response.status_code)

    def test_post_finish(self):
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            '%s-value' % self.value.pk: "rgba(255, 255, 255, 0)",
            '%s-style_property' % self.value.pk: self.value.style_property.pk,
            'finish': "Finish",
            }, follow=True)
        self.assertContains(
            response,
            "Updated %s" % self.value.style_version)
        self.assertRedirects(response, "%s?changed_id=%d" % (
            reverse('themes_list', urlconf='gbe.themes.urls'),
            self.value.style_version.pk))

    def test_post_update(self):
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            '%s-value' % self.value.pk: "rgba(255, 255, 255, 0)",
            '%s-style_property' % self.value.pk: self.value.style_property.pk,
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
                             reverse("themes_list", urlconf="gbe.themes.urls"))

    def test_post_basics_bad_data(self):
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            'finish': "Finish",
            }, follow=True)
        self.assertContains(response, self.title)
        self.assertContains(response, "There is an error on the form.")
        self.assertContains(response, self.style_url)
