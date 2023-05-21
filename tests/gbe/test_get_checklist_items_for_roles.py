from django.test import TestCase
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    NoEventRoleExclusionFactory
)
from tests.factories.gbe_factories import (
    BioFactory,
    ConferenceFactory,
    ProfileFactory
)
from scheduler.idd import get_schedule
from tests.functions.scheduler_functions import book_worker_item_for_role


class TestGetCheckListForRoles(TestCase):
    '''Tests that checklists are built based on roles'''

    @classmethod
    def setUpTestData(cls):
        cls.role_condition = RoleEligibilityConditionFactory()
        cls.teacher = BioFactory()
        cls.conference = ConferenceFactory()
        booking = book_worker_item_for_role(cls.teacher,
                                            cls.role_condition.role,
                                            conference=cls.conference)
        cls.schedule = get_schedule(
                cls.teacher.contact.user_object,
                labels=[cls.conference.conference_slug]).schedule_items

    def test_no_role(self):
        '''
            purchaser has no roles
        '''
        from gbe.ticketing_idd_interface import get_checklist_items_for_roles
        no_match_profile = ProfileFactory()
        no_schedule = get_schedule(
                no_match_profile.user_object,
                labels=[self.conference.conference_slug]).schedule_items
        checklist_items = get_checklist_items_for_roles(
            no_schedule,
            [])

        self.assertEqual(len(checklist_items), 0)

    def test_no_role_this_conference(self):
        '''
            purchaser has no roles in this conference
        '''
        from gbe.ticketing_idd_interface import get_checklist_items_for_roles
        checklist_items = get_checklist_items_for_roles([], [])

        self.assertEqual(len(checklist_items), 0)

    def test_role_match_happens(self):
        '''
            the profile fits the role, item is given
        '''
        from gbe.ticketing_idd_interface import get_checklist_items_for_roles
        checklist_items = get_checklist_items_for_roles(
            self.schedule,
            [])

        self.assertEqual(len(checklist_items), 1)
        self.assertEqual(checklist_items["Teacher"],
                         [self.role_condition.checklistitem])

    def test_multiple_role_match_happens(self):
        '''
            profile meets 2 role conditions
        '''
        from gbe.ticketing_idd_interface import get_checklist_items_for_roles
        another_role = RoleEligibilityConditionFactory(
            role="Staff Lead")

        booking = book_worker_item_for_role(
            self.teacher.contact,
            another_role.role,
            conference=self.conference
            )
        self.schedule = get_schedule(
                self.teacher.contact.user_object,
                labels=[self.conference.conference_slug]).schedule_items

        checklist_items = get_checklist_items_for_roles(
            self.schedule,
            [])

        self.assertEqual(len(checklist_items), 2)
        self.assertEqual(checklist_items['Teacher'],
                         [self.role_condition.checklistitem])
        self.assertEqual(checklist_items["Staff Lead"],
                         [another_role.checklistitem])
        another_role.delete()

    def test_role_match_two_conditions(self):
        '''
            two conditions match this circumstance
        '''
        from gbe.ticketing_idd_interface import get_checklist_items_for_roles
        another_match = RoleEligibilityConditionFactory()

        checklist_items = get_checklist_items_for_roles(
            self.schedule,
            [])

        self.assertEqual(len(checklist_items), 1)
        self.assertEqual(checklist_items["Teacher"],
                         [self.role_condition.checklistitem,
                         another_match.checklistitem])
        another_match.delete()

    def test_role_exclusion(self):
        '''
            a condition matches this circumstance, but is excluded
        '''
        from gbe.ticketing_idd_interface import get_checklist_items_for_roles
        exclusion = NoEventRoleExclusionFactory(
            condition=self.role_condition,
            role="Staff Lead")

        booking = book_worker_item_for_role(
            self.teacher.contact,
            exclusion.role,
            conference=self.conference
            )
        self.schedule = get_schedule(
                self.teacher.contact.user_object,
                labels=[self.conference.conference_slug]).schedule_items

        checklist_items = get_checklist_items_for_roles(
            self.schedule,
            [])

        self.assertEqual(len(checklist_items), 0)
