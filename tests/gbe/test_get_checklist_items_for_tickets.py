import nose.tools as nt
from django.test import TestCase
from tests.factories.ticketing_factories import (
    TicketingEligibilityConditionFactory,
    TicketingExclusionFactory,
    TransactionFactory
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory
)

from gbe.ticketing_idd_interface import get_checklist_items_for_tickets


class TestGetCheckListForTickets(TestCase):
    '''Tests that checklists are built based on ticket purchases'''

    def setUp(self):
        self.ticketingcondition = TicketingEligibilityConditionFactory()
        self.transaction = TransactionFactory()
        self.purchaser = ProfileFactory(
            user_object=self.transaction.purchaser.matched_to_user)
        self.conference = self.transaction.ticket_item.bpt_event.conference

    def test_no_ticket_condition(self):
        '''
            purchaser tickets have no conditions
        '''
        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference,
            [])
        nt.assert_equal(len(checklist_items), 0)

    def test_no_tickets_this_conference(self):
        '''
            list of tickets is empty, so there should be no match
        '''
        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference,
            [])
        nt.assert_equal(len(checklist_items), 0)

    def test_ticket_match_happens(self):
        '''
            feeding in the matching ticket, gives an item
        '''
        match_condition = TicketingEligibilityConditionFactory(
            tickets=[self.transaction.ticket_item])

        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference,
            [self.transaction.ticket_item])
        nt.assert_equal(len(checklist_items), 1)
        nt.assert_equal(checklist_items[0]['count'], 1)
        nt.assert_equal(checklist_items[0]['ticket'],
                        self.transaction.ticket_item.title)
        nt.assert_equal(checklist_items[0]['items'],
                        [match_condition.checklistitem])

    def test_multiple_ticket_match_happens(self):
        '''
            feeding in the matching ticket, gives an item
        '''
        match_condition = TicketingEligibilityConditionFactory(
            tickets=[self.transaction.ticket_item])
        another_transaction = TransactionFactory(
            purchaser=self.transaction.purchaser,
            ticket_item=self.transaction.ticket_item)

        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference,
            [self.transaction.ticket_item,
             another_transaction.ticket_item])
        nt.assert_equal(len(checklist_items), 1)
        nt.assert_equal(checklist_items[0]['count'], 2)
        nt.assert_equal(checklist_items[0]['ticket'],
                        self.transaction.ticket_item.title)
        nt.assert_equal(checklist_items[0]['items'],
                        [match_condition.checklistitem])

    def test_ticket_match_two_conditions(self):
        '''
            two conditions match this circumstance
        '''
        match_condition = TicketingEligibilityConditionFactory(
            tickets=[self.transaction.ticket_item])
        another_match = TicketingEligibilityConditionFactory(
            tickets=[self.transaction.ticket_item])

        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference,
            [self.transaction.ticket_item])
        nt.assert_equal(len(checklist_items), 1)
        nt.assert_equal(checklist_items[0]['count'], 1)
        nt.assert_equal(checklist_items[0]['ticket'],
                        self.transaction.ticket_item.title)
        nt.assert_equal(checklist_items[0]['items'],
                        [match_condition.checklistitem,
                         another_match.checklistitem])

    def test_ticket_is_excluded(self):
        '''
            there's a match, but also an exclusion
        '''
        match_condition = TicketingEligibilityConditionFactory(
            tickets=[self.transaction.ticket_item])
        exclusion = TicketingExclusionFactory(
            condition=match_condition,
            tickets=[self.transaction.ticket_item])

        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference,
            [])
        nt.assert_equal(len(checklist_items), 0)
