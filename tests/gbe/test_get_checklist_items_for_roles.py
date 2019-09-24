from django.http import Http404
from django.core.exceptions import PermissionDenied
import nose.tools as nt
from django.test import TestCase
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    NoEventRoleExclusionFactory
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory
)

from tests.functions.scheduler_functions import book_worker_item_for_role
from gbe.ticketing_idd_interface import get_checklist_items_for_roles


class TestGetCheckListForRoles(TestCase):
    '''Tests that checklists are built based on roles'''

    def setUp(self):
        self.role_condition = RoleEligibilityConditionFactory()
        self.teacher = PersonaFactory()
        booking = book_worker_item_for_role(self.teacher,
                                            self.role_condition.role)
        self.conference = booking.event.eventitem.get_conference()

    def test_no_role(self):
        '''
            purchaser has no roles
        '''
        no_match_profile = ProfileFactory()

        checklist_items = get_checklist_items_for_roles(
            no_match_profile,
            self.conference,
            [])

        nt.assert_equal(len(checklist_items), 0)

    def test_no_role_this_conference(self):
        '''
            purchaser has no roles in this conference
        '''
        checklist_items = get_checklist_items_for_roles(
            self.teacher.performer_profile,
            ConferenceFactory(),
            [])

        nt.assert_equal(len(checklist_items), 0)

    def test_role_match_happens(self):
        '''
            the profile fits the role, item is given
        '''

        checklist_items = get_checklist_items_for_roles(
            self.teacher.performer_profile,
            self.conference,
            [])

        nt.assert_equal(len(checklist_items), 1)
        nt.assert_equal(checklist_items["Teacher"],
                        [self.role_condition.checklistitem])

    def test_multiple_role_match_happens(self):
        '''
            profile meets 2 role conditions
        '''
        another_role = RoleEligibilityConditionFactory(
            role="Staff Lead")

        booking = book_worker_item_for_role(
            self.teacher.performer_profile,
            another_role.role,
            GenericEventFactory(
                e_conference=self.conference)
            )

        checklist_items = get_checklist_items_for_roles(
            self.teacher.performer_profile,
            self.conference,
            [])

        nt.assert_equal(len(checklist_items), 2)
        nt.assert_equal(checklist_items['Teacher'],
                        [self.role_condition.checklistitem])
        nt.assert_equal(checklist_items["Staff Lead"],
                        [another_role.checklistitem])
        another_role.delete()

    def test_role_match_two_conditions(self):
        '''
            two conditions match this circumstance
        '''

        another_match = RoleEligibilityConditionFactory()

        checklist_items = get_checklist_items_for_roles(
            self.teacher.performer_profile,
            self.conference,
            [])

        nt.assert_equal(len(checklist_items), 1)
        nt.assert_equal(checklist_items["Teacher"],
                        [self.role_condition.checklistitem,
                         another_match.checklistitem])
        another_match.delete()

    def test_role_exclusion(self):
        '''
            a condition matches this circumstance, but is excluded
        '''

        exclusion = NoEventRoleExclusionFactory(
            condition=self.role_condition,
            role="Staff Lead")

        booking = book_worker_item_for_role(
            self.teacher.performer_profile,
            exclusion.role,
            GenericEventFactory(
                e_conference=self.conference)
            )

        checklist_items = get_checklist_items_for_roles(
            self.teacher.performer_profile,
            self.conference,
            [])

        nt.assert_equal(len(checklist_items), 0)

    def tearDown(self):
        self.role_condition.delete()
