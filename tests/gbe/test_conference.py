from tests.factories.gbe_factories import (
    ConferenceFactory
)
from gbe.models import Conference
from django.test import TestCase


class TestConference(TestCase):
    def test_by_slug_gets_conf_for_given_slug(self):
        conf = ConferenceFactory(conference_slug="foo",
                                 status="not_ongoing")
        other_conf = ConferenceFactory(conference_slug="bar",
                                       status="ongoing")
        self.assertEqual(type(conf).by_slug("foo"), conf)

    def test_by_slug_gets_default_if_bad_slug_given(self):
        Conference.objects.all().delete()
        conf = ConferenceFactory(conference_slug="foo",
                                 status="not_ongoing")
        other_conf = ConferenceFactory(conference_slug="bar",
                                       status="ongoing")
        self.assertEqual(type(conf).by_slug("quux"), other_conf)
