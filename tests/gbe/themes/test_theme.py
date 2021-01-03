from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    StyleVersionFactory,
    StyleValueFactory,
)
from django.test.utils import override_settings


class TestTheme(TestCase):
    view_name = "theme_style"

    def setUp(self):
        self.client = Client()
        self.url = reverse(self.view_name, urlconf="gbe.themes.urls")

    def test_migrations(self):
        response = self.client.get(self.url)
        self.assertContains(
            response,
            ".gbe-alert-success {")
        self.assertContains(
            response,
            "    background-color: rgba(212, 237, 218, 1);")
        self.assertContains(
            response,
            "    border-color: rgba(195, 230, 203, 1);")
        self.assertContains(
            response,
            "    color: rgba(21, 87, 36, 1);")
        self.assertContains(
            response,
            "}")

    @override_settings(DEBUG=True)
    def test_special_test_style(self):
        version = StyleVersionFactory(currently_test=True)
        value = StyleValueFactory(style_version=version)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "%s {" % value.style_property.selector)
        self.assertContains(
            response,
            "    %s: %s" % (value.style_property.style_property,
                            value.value))
        self.assertNotContains(
            response,
            ".gbe-alert-success {")
        self.assertNotContains(
            response,
            "    background-color: rgba(212, 237, 218, 1);")

    @override_settings(DEBUG=True)
    def test_special_test_style_switch(self):
        version = StyleVersionFactory()
        version.currently_test = True
        version.save()
        value = StyleValueFactory(style_version=version)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "%s {" % value.style_property.selector)
        self.assertContains(
            response,
            "    %s: %s" % (value.style_property.style_property,
                            value.value))
        self.assertNotContains(
            response,
            ".gbe-alert-success {")
        self.assertNotContains(
            response,
            "    background-color: rgba(212, 237, 218, 1);")

    def test_special_live_style_switch(self):
        version = StyleVersionFactory()
        version.currently_live = True
        version.save()
        value = StyleValueFactory(style_version=version)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "%s {" % value.style_property.selector)
        self.assertContains(
            response,
            "    %s: %s" % (value.style_property.style_property,
                            value.value))
        self.assertNotContains(
            response,
            ".gbe-alert-success {")
        self.assertNotContains(
            response,
            "    background-color: rgba(212, 237, 218, 1);")
        self.assertEquals(
            str(version),
            "{} - version {:.1f}".format(version.name, version.number))
        self.assertEquals(
            str(value.style_property),
            "%s - %s" % (value.style_property.selector,
                         value.style_property.style_property))

    def test_ondemand_switch(self):
        version = StyleVersionFactory()
        version.save()
        value = StyleValueFactory(style_version=version)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[version.pk]))
        self.assertContains(
            response,
            "%s {" % value.style_property.selector)
        self.assertContains(
            response,
            "    %s: %s" % (value.style_property.style_property,
                            value.value))
        self.assertNotContains(
            response,
            ".gbe-alert-success {")
        self.assertNotContains(
            response,
            "    background-color: rgba(212, 237, 218, 1);")
        self.assertEquals(
            str(version),
            "{} - version {:.1f}".format(version.name, version.number))
        self.assertEquals(
            str(value.style_property),
            "%s - %s" % (value.style_property.selector,
                         value.style_property.style_property))
