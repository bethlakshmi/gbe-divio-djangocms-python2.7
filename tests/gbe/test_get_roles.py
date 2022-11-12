from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.contexts import StaffAreaContext
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    ShowFactory
)
from tests.functions.scheduler_functions import (
    book_act_item_for_show,
    book_worker_item_for_role)


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
        act = ActFactory(b_conference=self.conference,
                         accepted=3)
        show = ShowFactory(e_conference=self.conference)
        booking = book_act_item_for_show(
            act,
            show)
        profile = act.performer.performer_profile
        result = profile.get_roles(self.conference)
        self.assertEqual(result, ["Performer"])

    def test_teacher(self):
        '''
           has the role of a teacher, persona is booked for a class
        '''
        persona = PersonaFactory()
        booking = book_worker_item_for_role(
            persona,
            "Teacher")
        result = persona.performer_profile.get_roles(
            booking.event.eventitem.e_conference)
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
        this_class = GenericEventFactory(
            e_conference=self.conference)
        book_worker_item_for_role(
            persona,
            "Teacher",
            this_class)
        event = GenericEventFactory(
            e_conference=self.conference)
        book_worker_item_for_role(
            persona.performer_profile,
            "Staff Lead",
            event)
        act = ActFactory(b_conference=self.conference,
                         accepted=3,
                         performer=persona)
        show = ShowFactory(e_conference=self.conference)
        booking = book_act_item_for_show(act, show)

        result = persona.performer_profile.get_roles(
            self.conference)
        self.assertEqual(sorted(result),
                         ["Performer", "Staff Lead", "Teacher"])
