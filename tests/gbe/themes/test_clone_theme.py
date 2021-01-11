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
from decimal import Decimal
from gbe.models import StyleVersion


class TestCloneTheme(TestCase):
    view_name = "clone_theme"

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory().user_object
        grant_privilege(self.user, u'Theme Editor')
        self.value = StyleValueFactory()
        self.url = reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk])
        self.title = "Clone Styles Settings for {}, version {:.1f}".format(
            self.value.style_version.name,
            self.value.style_version.number)
        self.style_url = reverse(
            "theme_style",
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk])

    def get_post(self):
        return {
            '%s-value' % self.value.pk: "rgba(255, 255, 255, 0)",
            '%s-style_property' % self.value.pk: self.value.style_property.pk,
            'name': "Clone of " + self.value.style_version.name,
            'number': 1.0,
            }

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
        self.assertContains(
            response,
            '<input type="text" name="name" maxlength="128" required ' +
            'id="id_name">',
            html=True)
        self.assertContains(
            response,
            '<input type="number" name="number" value="1.0" min="0.1" ' +
            'step="any" required id="id_number">',
            html=True)

    def test_get_empty(self):
        empty = StyleVersionFactory()
        login_as(self.user, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[empty.pk]))
        self.assertContains(
            response,
            '<input type="text" name="name" maxlength="128" required ' +
            'id="id_name">',
            html=True)
        self.assertContains(
            response,
            '<input type="number" name="number" value="1.0" min="0.1" ' +
            'step="any" required id="id_number">',
            html=True)

    def test_post_finish(self):
        login_as(self.user, self)
        data = self.get_post()
        data['finish'] = 'Finish'
        response = self.client.post(self.url, data=data, follow=True)
        new_version = StyleVersion.objects.latest('pk')
        print(response.content)
        self.assertContains(
            response,
            "Cloned %s from %s" % (new_version,
                                   self.value.style_version))
        self.assertRedirects(response, "%s?changed_id=%d" % (
            reverse('themes_list', urlconf='gbe.themes.urls'),
            new_version.pk))

    def test_post_update(self):
        login_as(self.user, self)
        data = self.get_post()
        data['update'] = 'Update'
        response = self.client.post(self.url, data=data, follow=True)
        new_version = StyleVersion.objects.latest('pk')
        print(response.content)
        self.assertContains(
            response,
            "Manage Styles Settings for {}, version {:.1f}".format(
                new_version.name,
                new_version.number))
        self.assertContains(
            response,
            "Cloned %s from %s" % (new_version,
                                   self.value.style_version))
        self.assertRedirects(response, reverse(
            "manage_theme", 
            urlconf="gbe.themes.urls",
            args=[new_version.pk]))
        self.assertContains(response, 'rgba(255, 255, 255, 0)')
        self.assertContains(response,
                            self.value.style_property.selector)
        self.assertContains(response,
                            self.value.style_property.selector.used_for)
        self.assertContains(response,
                            self.value.style_property.style_property)

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

    def test_post_basics_bad_theme_version(self):
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            'name': self.value.style_version.name,
            'version': self.value.style_version.number,
            'finish': "Finish",
            }, follow=True)
        self.assertContains(response, self.title)
        self.assertContains(response, "There is an error on the form.")
        self.assertContains(response, self.style_url)
