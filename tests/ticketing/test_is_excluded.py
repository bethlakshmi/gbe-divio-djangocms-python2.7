from django.core.exceptions import PermissionDenied
from ticketing.models import *
import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
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
from tests.functions.scheduler_functions import book_worker_item_for_role
from scheduler.idd import get_schedule
from tests.functions.gbe_functions import clear_conferences


class TestIsExcluded(TestCase):
    '''Tests for exclusions in all Exclusion subclasses'''

    def setUp(self):
        clear_conferences()
        self.factory = RequestFactory()
        self.client = Client()
        self.ticketingexclusion = TicketingExclusionFactory.create()
        self.roleexclusion = RoleExclusionFactory.create()
        self.teacher = PersonaFactory.create()
        booking = book_worker_item_for_role(
            self.teacher,
            self.roleexclusion.role,
            )
        self.roleexclusion.event = booking.event.eventitem
        self.roleexclusion.save()
        self.conference = booking.event.eventitem.get_conference()
        self.schedule = get_schedule(
                self.teacher.performer_profile.user_object,
                labels=[self.conference.conference_slug]).schedule_items

    def test_no_ticket_excluded(self):
        '''
            the ticket is not in the excluded set
        '''
        diff_ticket = TicketItemFactory.create()
        nt.assert_false(self.ticketingexclusion.is_excluded([diff_ticket]))

    def test_ticket_is_excluded(self):
        '''
           a ticket in the held tickets matches the exclusion set
        '''
        problem_ticket = TicketItemFactory.create()
        self.ticketingexclusion.tickets.add(problem_ticket)
        nt.assert_true(
            self.ticketingexclusion.is_excluded([problem_ticket]))

    def test_role_is_excluded(self):
        '''
           role matches, no event is present, exclusion happens
        '''
        no_event = NoEventRoleExclusionFactory.create()
        nt.assert_true(no_event.is_excluded(self.schedule))

    def test_role_not_event(self):
        '''
           role matches but event does not, not excluded
        '''
        new_exclude = RoleExclusionFactory.create()
        nt.assert_false(new_exclude.is_excluded(self.schedule))

    def test_no_role_match(self):
        '''
            role does not match, not excluded
        '''
        no_event = NoEventRoleExclusionFactory.create(role="Vendor")
        nt.assert_false(no_event.is_excluded(self.schedule))

    def test_role_and_event_match(self):
        '''
            role and event match the exclusion
        '''
        nt.assert_true(self.roleexclusion.is_excluded(self.schedule))

    def test_condition_ticket_exclusion(self):
        '''
            condition has a ticketing exclusion, which is triggered
        '''
        problem_ticket = TicketItemFactory.create()
        self.ticketingexclusion.tickets.add(problem_ticket)
        nt.assert_true(
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
        nt.assert_true(self.roleexclusion.condition.is_excluded(
            [],
            self.schedule))

    def test_condition_role_exclusion_no_event(self):
        '''
            condition does not have any exclusions for this particular case
        '''
        no_event = NoEventRoleExclusionFactory.create(role="Vendor")
        nt.assert_false(no_event.condition.is_excluded(
            [],
            self.schedule))

    def tearDown(self):
        self.ticketingexclusion.delete()
        self.roleexclusion.delete()
        self.teacher.delete()
        self.conference.delete()
