from django.test import TestCase
from django.urls import reverse

from cms.api import add_plugin
from cms.models import Placeholder

from gbe.cms_plugins import (
    ContactFormPlugin,
    NewsPlugin,
)
from gbe.forms import ContactForm
from tests.factories.gbe_factories import ArticleFactory


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


class NewsPluginTests(TestCase):

    def test_plugin_context(self):
        ArticleFactory.create_batch(10)
        placeholder = Placeholder.objects.create(slot='test')
        model_instance = add_plugin(
            placeholder,
            NewsPlugin,
            'en',
        )
        plugin_instance = model_instance.get_plugin_class_instance()
        context = plugin_instance.render({}, model_instance, None)
        self.assertIn('object_list', context)
        # default for # of articles to show is 4
        self.assertEqual(len(context['object_list']), 4)
        self.assertEqual(context['more'], True)
