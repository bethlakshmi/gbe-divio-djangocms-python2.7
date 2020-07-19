from django.test import TestCase
from django.urls import reverse

from cms.api import add_plugin
from cms.models import Placeholder

from gbe.cms_plugins import (
    ClassIdeaPlugin,
    ContactFormPlugin,
)
from gbe.forms import (
    ContactForm,
    ClassProposalForm,
)


class ClassIdeaPluginTests(TestCase):

    def test_plugin_context(self):
        placeholder = Placeholder.objects.create(slot='test')
        model_instance = add_plugin(
            placeholder,
            ClassIdeaPlugin,
            'en',
        )
        plugin_instance = model_instance.get_plugin_class_instance()
        context = plugin_instance.render({}, model_instance, None)
        self.assertIn('forms', context)
        self.assertEqual(type(context['forms'][0]),
                         type(ClassProposalForm()))
        self.assertEqual(len(context['forms']), 1)
        self.assertIn('bid_destination', context)
        self.assertEqual(context['bid_destination'],
                         reverse('class_propose',
                                 urlconf='gbe.urls'))
        self.assertIn('nodraft', context)
        self.assertEqual(context['nodraft'], 'Submit')


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
