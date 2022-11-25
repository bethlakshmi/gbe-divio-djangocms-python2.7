from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
)
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.scheduler_functions import book_worker_item_for_role


class TestGetRoles(TestCase):
    '''Tests that a profile will return all the possible roles'''

    @classmethod
    def setUpTestData(cls):
        cls.conference = ConferenceFactory()

    def test_basic_profile(self):
        '''
           Simplest user - just has a profile, doesn't have any role
        '''
        profile = ProfileFactory()
        result = profile.get_roles(self.conference)
        self.assertEqual(len(result), 0)

    def test_basic_persona(self):
        '''
           Has a performer/teacher identity, but no commitment so no role
        '''
        persona = PersonaFactory()
        result = persona.performer_profile.get_roles(self.conference)
        self.assertEqual(len(result), 0)

    def test_unbooked_performer(self):
        '''
            Submitted an act, didn't make it to a show
        '''
        act = ActFactory(b_conference=self.conference)
        profile = act.performer.performer_profile
        result = profile.get_roles(self.conference)
        self.assertEqual(len(result), 0)

    def test_booked_performer(self):
        '''
           has the role of performer from being booked in a show
        '''
        context = ShowContext(conference=self.conference)
        profile = context.acts[0].performer.performer_profile
        result = profile.get_roles(self.conference)
        self.assertEqual(result, ["Performer"])

    def test_teacher(self):
        '''
           has the role of a teacher, persona is booked for a class
        '''
        persona = PersonaFactory()
        booking = book_worker_item_for_role(
            persona,
            "Teacher",
            conference=self.conference)
        result = persona.performer_profile.get_roles(
            self.conference)
        self.assertEqual(result, ["Teacher"])

    def test_staff_lead(self):
        '''
           has the role of a teacher, persona is booked for a class
        '''
        context = StaffAreaContext()
        result = context.staff_lead.get_roles(
            context.conference)
        self.assertEqual(result, ["Staff Lead"])

    def test_overcommitment_addict(self):
        '''
           1 of every permutation possible to link people to roles
        '''
        persona = PersonaFactory()
        this_class = ClassContext(conference=self.conference,
                                  teacher=persona)
        book_worker_item_for_role(
            persona.performer_profile,
            "Staff Lead",
            conference=self.conference)
        act = ActFactory(b_conference=self.conference,
                         accepted=3,
                         performer=persona)
        showcontext = ShowContext(act=act, conference=self.conference)

        result = persona.performer_profile.get_roles(
            self.conference)
        self.assertEqual(sorted(result),
                         ["Performer", "Staff Lead", "Teacher"])
