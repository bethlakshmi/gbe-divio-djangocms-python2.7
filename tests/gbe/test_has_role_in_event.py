from django.test import TestCase
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.scheduler_functions import book_worker_item_for_role
from tests.contexts import (
    ShowContext,
)

class TestHasRoleInEvent(TestCase):
    '''Tests that a profile will return all the possible roles'''

    @classmethod
    def setUpTestData(cls):
        cls.persona = PersonaFactory()
        cls.role = "Teacher"
        cls.booking = book_worker_item_for_role(cls.persona,
                                                cls.role)

    def test_basic_profile_teacher(self):
        '''
           Simplest user - just has a profile, doesn't have any booking
        '''
        profile = ProfileFactory()
        result = profile.has_role_in_event(self.role,
                                           self.booking.event)
        self.assertFalse(result)

    def test_unbooked_performer(self):
        '''
            Submitted an act, didn't make it to a show
        '''
        act = ActFactory()
        profile = act.performer.performer_profile
        result = profile.has_role_in_event("Performer",
                                           self.booking.event)
        self.assertFalse(result)

    def test_booked_performer(self):
        '''
           has the role of performer from being booked in a show
        '''
        context = ShowContext()
        profile = context.acts[0].performer.performer_profile
        result = profile.has_role_in_event("Performer",
                                           context.sched_event)
        self.assertTrue(result)

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
            booking.event)
        self.assertTrue(result)
