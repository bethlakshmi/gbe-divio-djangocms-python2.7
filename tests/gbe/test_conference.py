import pytest
from tests.factories.gbe_factories import (
    ConferenceFactory
)
from gbe.models import Conference
import nose.tools as nt


@pytest.mark.django_db
def test_by_slug_gets_conf_for_given_slug():
    conf = ConferenceFactory(conference_slug="foo",
                             status="not_ongoing")
    other_conf = ConferenceFactory(conference_slug="bar",
                                   status="ongoing")
    nt.assert_equal(type(conf).by_slug("foo"), conf)


@pytest.mark.django_db
def test_by_slug_gets_default_if_bad_slug_given():
    Conference.objects.all().delete()
    conf = ConferenceFactory(conference_slug="foo",
                             status="not_ongoing")
    other_conf = ConferenceFactory(conference_slug="bar",
                                   status="ongoing")
    nt.assert_equal(type(conf).by_slug("quux"), other_conf)
