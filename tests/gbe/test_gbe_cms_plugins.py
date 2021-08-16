from django.test import TestCase
from django.urls import reverse

from cms.api import add_plugin
from cms.models import Placeholder

from gbe.cms_plugins import ContactFormPlugin
from gbe.forms import ContactForm


class ContactFormPluginTests(TestCase):

    def test_plugin_context(self):
        placeholder = Placeholder.objects.create(slot='test')
        model_instance = add_plugin(
            placeholder,
            ContactFormPlugin,
            'en',
        )
        plugin_instance = model_instance.get_plugin_class_instance()
        context = plugin_instance.render({}, model_instance, None)
        self.assertIn('contact_form', context)
        self.assertEqual(type(context['contact_form']),
                         type(ContactForm()))
