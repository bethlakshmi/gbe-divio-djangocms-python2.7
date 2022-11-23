from ticketing.models import *
from django.test import TestCase
from django.test import Client
from tests.factories.ticketing_factories import (
    TicketingExclusionFactory,
    RoleExclusionFactory,
    TicketItemFactory,
    NoEventRoleExclusionFactory
)
from tests.factories.gbe_factories import (
    PersonaFactory
)
from gbe.models import Conference
from tests.functions.scheduler_functions import book_worker_item_for_role
from scheduler.idd import get_schedule
from tests.functions.gbe_functions import clear_conferences


class TestIsExcluded(TestCase):
    '''Tests for exclusions in all Exclusion subclasses'''

    @classmethod
    def setUpTestData(cls):
        clear_conferences()
        cls.ticketingexclusion = TicketingExclusionFactory.create()
        cls.roleexclusion = RoleExclusionFactory.create()
        cls.teacher = PersonaFactory.create()
        booking = book_worker_item_for_role(
            cls.teacher,
            cls.roleexclusion.role,
            )
        cls.roleexclusion.event = booking.event
        cls.roleexclusion.save()
        cls.conference = Conference.objects.filter(
            conference_slug__in=booking.event.labels)[0]
        cls.schedule = get_schedule(
                cls.teacher.performer_profile.user_object,
                labels=[cls.conference.conference_slug]).schedule_items

    def setUp(self):
        self.client = Client()

    def test_no_ticket_excluded(self):
        '''
            the ticket is not in the excluded set
        '''
        diff_ticket = TicketItemFactory.create()
        self.assertFalse(self.ticketingexclusion.is_excluded([diff_ticket]))

    def test_ticket_is_excluded(self):
        '''
           a ticket in the held tickets matches the exclusion set
        '''
        problem_ticket = TicketItemFactory.create()
        self.ticketingexclusion.tickets.add(problem_ticket)
        self.assertTrue(
            self.ticketingexclusion.is_excluded([problem_ticket]))

    def test_role_is_excluded(self):
        '''
           role matches, no event is present, exclusion happens
        '''
        no_event = NoEventRoleExclusionFactory.create()
        self.assertTrue(no_event.is_excluded(self.schedule))

    def test_role_not_event(self):
        '''
           role matches but event does not, not excluded
        '''
        new_exclude = RoleExclusionFactory.create()
        self.assertFalse(new_exclude.is_excluded(self.schedule))

    def test_no_role_match(self):
        '''
            role does not match, not excluded
        '''
        no_event = NoEventRoleExclusionFactory.create(role="Vendor")
        self.assertFalse(no_event.is_excluded(self.schedule))

    def test_role_and_event_match(self):
        '''
            role and event match the exclusion
        '''
        self.assertTrue(self.roleexclusion.is_excluded(self.schedule))

    def test_condition_ticket_exclusion(self):
        '''
            condition has a ticketing exclusion, which is triggered
        '''
        problem_ticket = TicketItemFactory.create()
        self.ticketingexclusion.tickets.add(problem_ticket)
        self.assertTrue(
            self.ticketingexclusion.condition.is_excluded(
                [problem_ticket],
                self.schedule
                ))

    def test_condition_role_exclusion(self):
        '''
            condition has a role exclusion, and no tickets are provided
        '''
        problem_ticket = TicketItemFactory.create()
        self.ticketingexclusion.tickets.add(problem_ticket)
        self.assertTrue(self.roleexclusion.condition.is_excluded(
            [],
            self.schedule))

    def test_condition_role_exclusion_no_event(self):
        '''
            condition does not have any exclusions for this particular case
        '''
        no_event = NoEventRoleExclusionFactory.create(role="Vendor")
        self.assertFalse(no_event.condition.is_excluded(
            [],
            self.schedule))
