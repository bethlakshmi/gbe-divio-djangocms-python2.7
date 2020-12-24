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
        self.url = reverse(self.view_name, urlconf="gbe.urls")

    def test_migrations(self):
        response = self.client.get(self.url)
        self.assertContains(
            response,
            ".gbe-alert-success {")
        self.assertContains(
            response,
            "    background-color: #d4edda;")
        self.assertContains(
            response,
            "    border-color: #c3e6cb;")
        self.assertContains(
            response,
            "    color: #155724;")
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
            "    background-color: #d4edda;")

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
            "    background-color: #d4edda;")

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
            "    background-color: #d4edda;")
        self.assertEquals(
            str(version), "%s - version %d" % (version.name, version.number))
        self.assertEquals(
            str(value.style_property),
            "%s - %s" % (value.style_property.selector,
                         value.style_property.style_property))
