from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    StyleVersionFactory,
    UserStylePreviewFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe.models import UserStylePreview


class TestPreviewTheme(TestCase):
    view_name = "preview_theme"

    def setUp(self):
        UserStylePreview.objects.all().delete()
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

    def test_set_preview(self):
        login_as(self.user, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, "%s?changed_id=%d" % (
            self.return_url,
            self.version.pk))
        self.assertContains(response, self.title)
        self.assertContains(
            response,
            "Setting preview version to: " + str(self.version))
        self.assertNotContains(
            response,
            reverse(self.view_name,
                    urlconf="gbe.themes.urls",
                    args=[self.version.pk]))
        self.assertContains(
            response,
            'href="%s"' % reverse(
                "preview_off",
                urlconf="gbe.themes.urls"),
            count=1)

    def test_change_preview(self):
        UserStylePreviewFactory(version=self.active_version,
                                previewer=self.user)
        login_as(self.user, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, "%s?changed_id=%d" % (
            self.return_url,
            self.version.pk))
        self.assertContains(response, self.title)
        self.assertContains(
            response,
            "Setting preview version to: " + str(self.version))
        self.assertNotContains(
            response,
            reverse(self.view_name,
                    urlconf="gbe.themes.urls",
                    args=[self.version.pk]))
        self.assertContains(
            response,
            'href="%s"' % reverse(
                "preview_off",
                urlconf="gbe.themes.urls"),
            count=1)
        self.assertContains(
            response,
            reverse(self.view_name,
                    urlconf="gbe.themes.urls",
                    args=[self.active_version.pk]))

    def test_preview_bad_id(self):
        login_as(self.user, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[self.active_version.pk+1]))
        self.assertEqual(404, response.status_code)

    def test_turn_off_preview(self):
        UserStylePreviewFactory(version=self.version,
                                previewer=self.user)
        login_as(self.user, self)
        response = self.client.get(
            reverse("preview_off", urlconf="gbe.themes.urls"),
            follow=True)
        self.assertRedirects(response, "%s?changed_id=%d" % (
            self.return_url,
            self.version.pk))
        self.assertContains(response, self.title)
        self.assertContains(
            response,
            "Deactivating preview of version: " + str(self.version))
        self.assertContains(
            response,
            reverse(self.view_name,
                    urlconf="gbe.themes.urls",
                    args=[self.version.pk]))
        self.assertNotContains(
            response,
            'href="%s"' % reverse(
                "preview_off",
                urlconf="gbe.themes.urls"))
        self.assertContains(
            response,
            reverse(self.view_name,
                    urlconf="gbe.themes.urls",
                    args=[self.active_version.pk]))

    def test_turn_off_no_preview(self):
        login_as(self.user, self)
        response = self.client.get(
            reverse("preview_off", urlconf="gbe.themes.urls"),
            follow=True)
        self.assertRedirects(response, self.return_url)
        self.assertContains(response, self.title)
        self.assertNotContains(
            response,
            "Deactivating preview of version: " + str(self.version))
        self.assertContains(
            response,
            reverse(self.view_name,
                    urlconf="gbe.themes.urls",
                    args=[self.version.pk]))
        self.assertNotContains(
            response,
            'href="%s"' % reverse(
                "preview_off",
                urlconf="gbe.themes.urls"))
        self.assertContains(
            response,
            reverse(self.view_name,
                    urlconf="gbe.themes.urls",
                    args=[self.active_version.pk]))
