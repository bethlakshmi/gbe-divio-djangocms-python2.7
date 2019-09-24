import nose.tools as nt
from django.test import TestCase

from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    ShowFactory
)
from tests.functions.scheduler_functions import (
    book_act_item_for_show,
    book_worker_item_for_role,
)


class TestHasRoleInEvent(TestCase):
    '''Tests that a profile will return all the possible roles'''

    def setUp(self):
        self.persona = PersonaFactory()
        self.role = "Teacher"
        self.booking = book_worker_item_for_role(self.persona,
                                                 self.role)

    def test_basic_profile_teacher(self):
        '''
           Simplest user - just has a profile, doesn't have any booking
        '''
        profile = ProfileFactory()
        result = profile.has_role_in_event(self.role,
                                           self.booking.event.eventitem)
        nt.assert_false(result)

    def test_unbooked_performer(self):
        '''
            Submitted an act, didn't make it to a show
        '''
        act = ActFactory()
        profile = act.performer.performer_profile
        result = profile.has_role_in_event("Performer",
                                           self.booking)
        nt.assert_false(result)

    def test_booked_performer(self):
        '''
           has the role of performer from being booked in a show
        '''
        act = ActFactory(accepted=3)
        show = ShowFactory()
        booking = book_act_item_for_show(
            act,
            show)
        profile = act.performer.performer_profile
        result = profile.has_role_in_event("Performer",
                                           show)
        nt.assert_true(result)

    def test_teacher(self):
        '''
           has the role of a teacher, persona is booked for a class
        '''
        persona = PersonaFactory()
        booking = book_worker_item_for_role(
            persona,
            "Teacher")
        result = persona.performer_profile.has_role_in_event(
            "Teacher",
            booking.event.eventitem)
        nt.assert_true(result)
