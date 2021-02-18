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
from gbe.models import StyleVersion


class TestThemesList(TestCase):
    '''Tests for review_costume_list view'''
    view_name = "themes_list"

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory().user_object
        grant_privilege(self.user, u'Theme Editor')
        self.version = StyleVersionFactory(currently_live=True,
                                           currently_test=True)
        self.url = reverse(self.view_name, urlconf="gbe.themes.urls")

    def test_no_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             "/login/?next=%s" % self.url,
                             fetch_redirect_response=False)

    def test_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_list_basic(self):
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.version.name)
        self.assertContains(response, reverse(
            "manage_theme",
            urlconf="gbe.themes.urls",
            args=[self.version.pk]))
        self.assertContains(
            response,
            '<i class="gbe-text-success fas fa-check-circle"',
            2)
        self.assertContains(response, reverse(
            "preview_theme",
            urlconf="gbe.themes.urls",
            args=[self.version.pk]))
        self.assertContains(response, reverse(
            "clone_theme",
            urlconf="gbe.themes.urls",
            args=[self.version.pk]))

    def test_list_all_the_things(self):
        boring_version = StyleVersionFactory()
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.version.name)
        self.assertContains(response, boring_version.name)
        self.assertContains(
            response,
            '<i class="gbe-text-success fas fa-check-circle"',
            2)
        self.assertContains(response, reverse(
            "manage_theme",
            urlconf="gbe.themes.urls",
            args=[self.version.pk]))
        self.assertContains(response, reverse(
            "manage_theme",
            urlconf="gbe.themes.urls",
            args=[boring_version.pk]))
        self.assertContains(response, reverse(
            "clone_theme",
            urlconf="gbe.themes.urls",
            args=[self.version.pk]))
        self.assertContains(response, reverse(
            "clone_theme",
            urlconf="gbe.themes.urls",
            args=[boring_version.pk]))

    def test_list_w_no_items(self):
        StyleVersion.objects.all().delete()
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, "List of Themes and Versions")

    def test_show_changed(self):
        login_as(self.user, self)
        response = self.client.get(
            "%s?changed_id=%d" % (self.url, self.version.pk))
        self.assertContains(response, "gbe-table-success")

    def test_show_error(self):
        login_as(self.user, self)
        response = self.client.get(
            "%s?error_id=%d" % (self.url, self.version.pk))
        print(response.content)
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-error"><td>%d</td>' % (
                self.version.pk))

    def test_user_has_preview(self):
        UserStylePreviewFactory(version=self.version, previewer=self.user)
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.version.name)
        self.assertNotContains(response, reverse(
            "preview_theme",
            urlconf="gbe.themes.urls",
            args=[self.version.pk]))
        self.assertContains(
            response,
            'href="%s"' % reverse(
                "preview_off",
                urlconf="gbe.themes.urls"),
            count=1)
