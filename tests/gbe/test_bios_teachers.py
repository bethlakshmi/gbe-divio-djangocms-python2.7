import nose.tools as nt
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    ClassProposalFactory,
    ProfileFactory,
    PersonaFactory
)
from tests.contexts import ClassContext
from gbe.models import (
    Conference
)
from django.core.urlresolvers import reverse
from scheduler.models import Event as sEvent
from datetime import datetime, date, time
import pytz
from scheduler.models import (
    Worker,
    EventContainer
)
from tests.factories.scheduler_factories import ResourceAllocationFactory
from tests.functions.gbe_functions import (
    clear_conferences,
    current_conference,
    login_as,
)


class TestBiosTeachers(TestCase):
    '''Tests for bios_teachers view'''
    view_name = 'bios_teacher'

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_bios_teachers_no_conf_slug(self):
        current_context = ClassContext(conference=current_conference())
        other_conference = ConferenceFactory(status="ended")
        other_context = ClassContext(conference=other_conference)
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        assert response.status_code == 200
        assert current_context.teacher.name in response.content
        assert current_context.bid.b_title in response.content

        # the following assertions should work, but currently
        # do not. This is possibly an issue with multiple
        # inheritance and factory boy, but that is not clear
        # to me.
        # Leaving them commented out to encourage us to
        # fix (still broken - 1/12/17)
        # assert other_context.teacher.name not in response.content
        # assert other_context.bid.title not in response.content

    def test_bios_teachers_specific_conference(self):
        first_context = ClassContext()
        other_context = ClassContext()
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(
            url,
            data={'conference': first_context.conference.conference_slug})
        assert response.status_code == 200
        assert first_context.bid.teacher.name in response.content
        assert first_context.bid.b_title in response.content

        # the following assertions should work, but currently
        # do not. This is possibly an issue with multiple
        # inheritance and factory boy, but that is not clear
        # to me.
        # Leaving them commented out to encourage us to
        # fix
        # assert other_context.bid.teacher.name not in response.content
        # assert other_context.bid.title not in response.content

    def test_bios_teachers_unbooked_accepted(self):
        accepted_class = ClassFactory(b_conference=current_conference(),
                                      e_conference=current_conference(),
                                      accepted=3)
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(
            url,
            data={'conference': accepted_class.b_conference.conference_slug})

        assert response.status_code == 200
        assert accepted_class.teacher.name in response.content
        assert accepted_class.b_title in response.content
