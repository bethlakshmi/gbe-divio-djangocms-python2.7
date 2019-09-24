import nose.tools as nt
from django.test import TestCase
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    PurchaserFactory,
    TicketingEligibilityConditionFactory,
    TransactionFactory
)
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory
)

from tests.functions.scheduler_functions import book_worker_item_for_role
from gbe.ticketing_idd_interface import get_checklist_items


class TestGetCheckListItems(TestCase):
    '''Tests for the biggest method to get all types of checklist items'''

    def setUp(self):
        self.role_condition = RoleEligibilityConditionFactory()
        self.ticket_condition = TicketingEligibilityConditionFactory()

    def test_no_checklist(self):
        '''
            profile matches no conditions
        '''
        no_match_profile = ProfileFactory()
        transaction = TransactionFactory()
        self.ticket_condition.tickets.add(transaction.ticket_item)
        ticket_items, role_items = get_checklist_items(
            no_match_profile,
            transaction.ticket_item.bpt_event.conference)

        nt.assert_equal(len(ticket_items), 0)
        nt.assert_equal(len(role_items), 0)

    def test_role_match(self):
        '''
            profile has a role match condition
        '''
        teacher = PersonaFactory()
        booking = book_worker_item_for_role(teacher,
                                            self.role_condition.role)
        conference = booking.event.eventitem.get_conference()

        ticket_items, role_items = get_checklist_items(
            teacher.performer_profile,
            conference)
        nt.assert_equal(len(role_items), 1)
        nt.assert_equal(role_items[self.role_condition.role],
                        [self.role_condition.checklistitem])

    def test_ticket_match(self):
        '''
            profile has a ticket match condition
        '''
        transaction = TransactionFactory()
        purchaser = ProfileFactory(
            user_object=transaction.purchaser.matched_to_user)
        conference = transaction.ticket_item.bpt_event.conference
        self.ticket_condition.tickets.add(transaction.ticket_item)
        self.ticket_condition.save()

        ticket_items, role_items = get_checklist_items(
            purchaser,
            conference)

        nt.assert_equal(len(ticket_items), 1)
        nt.assert_equal(ticket_items[0]['items'],
                        [self.ticket_condition.checklistitem])

    def test_both_match(self):
        '''
            profile meets role and ticket
        '''
        teacher = PersonaFactory()
        booking = book_worker_item_for_role(teacher,
                                            self.role_condition.role)
        conference = booking.event.eventitem.get_conference()

        purchaser = PurchaserFactory(
            matched_to_user=teacher.performer_profile.user_object)
        transaction = TransactionFactory(
            purchaser=purchaser)
        transaction.ticket_item.bpt_event.conference = conference
        transaction.ticket_item.bpt_event.save()
        self.ticket_condition.tickets.add(transaction.ticket_item)
        self.ticket_condition.save()

        ticket_items, role_items = get_checklist_items(
            teacher.performer_profile,
            conference)
        nt.assert_equal(len(ticket_items), 1)
        nt.assert_equal(len(role_items), 1)
        nt.assert_equal(ticket_items[0]['ticket'],
                        transaction.ticket_item.title)
        nt.assert_equal(role_items[self.role_condition.role],
                        [self.role_condition.checklistitem])

    def tearDown(self):
        self.role_condition.delete()
        self.ticket_condition.delete()
