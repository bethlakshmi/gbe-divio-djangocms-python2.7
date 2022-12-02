from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    StyleVersionFactory,
)
from gbe.models import StyleVersion
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbetext import user_messages


class TestDeleteTheme(TestCase):
    view_name = "delete_theme"
    delete_link = '<a class="gbe-detail" href="%s" title="Delete">'

    def setUp(self):
        StyleVersion.objects.all().delete()
        self.client = Client()
        self.user = ProfileFactory().user_object
        grant_privilege(self.user, u'Theme Editor')
        self.version = StyleVersionFactory()
        self.active_version = StyleVersionFactory(currently_live=True,
                                                  currently_test=True)
        self.url = reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[self.version.pk])
        self.return_url = reverse("themes_list", urlconf="gbe.themes.urls")
        self.title = "List of Themes and Versions"

    def test_no_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             "%s?next=%s" % (reverse('login'), self.url),
                             fetch_redirect_response=False)

    def test_delete_succeed(self):
        login_as(self.user, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.return_url)
        self.assertContains(response, self.title)
        self.assertContains(response, "Deleted Theme %s" % str(self.version))
        self.assertNotContains(
            response,
            self.delete_link % reverse(
                self.view_name,
                urlconf="gbe.themes.urls",
                args=[self.version.pk]))

    def test_delete_bad_id(self):
        login_as(self.user, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[self.active_version.pk+1]))
        self.assertEqual(404, response.status_code)

    def test_delete_active_theme(self):
        login_as(self.user, self)
        self.url = reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[self.active_version.pk])
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            "%s?error_id=%d" % (self.return_url, self.active_version.pk))
        self.assertContains(response, self.title)
        self.assertContains(
            response,
            user_messages["CURRENTLY_ACTIVE"]['description'] + "  TARGET: " +
            str(self.active_version))
        self.assertContains(
            response,
            self.delete_link % reverse(
                self.view_name,
                urlconf="gbe.themes.urls",
                args=[self.active_version.pk]))

    def test_delete_last_theme(self):
        login_as(self.user, self)
        self.active_version.delete()
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            "%s?error_id=%d" % (self.return_url, self.version.pk))
        self.assertContains(response, self.title)
        self.assertContains(
            response,
            user_messages["LAST_THEME"]['description'] + "  TARGET: " +
            str(self.version))
        self.assertContains(
            response,
            self.delete_link % reverse(
                self.view_name,
                urlconf="gbe.themes.urls",
                args=[self.version.pk]))
