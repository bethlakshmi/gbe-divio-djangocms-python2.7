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
from scheduler.idd import get_schedule
from tests.functions.scheduler_functions import book_worker_item_for_role
from gbe.ticketing_idd_interface import get_checklist_items


class TestGetCheckListItems(TestCase):
    '''Tests for the biggest method to get all types of checklist items'''

    @classmethod
    def setUpTestData(cls):
        cls.role_condition = RoleEligibilityConditionFactory()
        cls.ticket_condition = TicketingEligibilityConditionFactory()

    def test_no_checklist(self):
        '''
            profile matches no conditions
        '''
        no_match_profile = ProfileFactory()
        transaction = TransactionFactory()
        conf = transaction.ticket_item.ticketing_event.conference
        self.ticket_condition.tickets.add(transaction.ticket_item)
        no_schedule = get_schedule(
                no_match_profile.user_object,
                labels=[conf.conference_slug]).schedule_items
        ticket_items, role_items = get_checklist_items(
            no_match_profile,
            transaction.ticket_item.ticketing_event.conference,
            no_schedule)

        self.assertEqual(len(ticket_items), 0)
        self.assertEqual(len(role_items), 0)

    def test_role_match(self):
        '''
            profile has a role match condition
        '''
        teacher = PersonaFactory()
        booking = book_worker_item_for_role(teacher,
                                            self.role_condition.role)
        conference = booking.event.eventitem.get_conference()
        self.schedule = get_schedule(
                teacher.performer_profile.user_object,
                labels=[conference.conference_slug]).schedule_items

        ticket_items, role_items = get_checklist_items(
            teacher.performer_profile,
            conference,
            self.schedule)
        self.assertEqual(len(role_items), 1)
        self.assertEqual(role_items[self.role_condition.role],
                        [self.role_condition.checklistitem])

    def test_ticket_match(self):
        '''
            profile has a ticket match condition
        '''
        transaction = TransactionFactory()
        purchaser = ProfileFactory(
            user_object=transaction.purchaser.matched_to_user)
        conference = transaction.ticket_item.ticketing_event.conference
        self.ticket_condition.tickets.add(transaction.ticket_item)
        self.ticket_condition.save()
        self.schedule = get_schedule(
                purchaser.user_object,
                labels=[conference.conference_slug]).schedule_items

        ticket_items, role_items = get_checklist_items(
            purchaser,
            conference,
            self.schedule)

        self.assertEqual(len(ticket_items), 1)
        self.assertEqual(ticket_items[0]['items'],
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
        transaction.ticket_item.ticketing_event.conference = conference
        transaction.ticket_item.ticketing_event.save()
        self.ticket_condition.tickets.add(transaction.ticket_item)
        self.ticket_condition.save()

        self.schedule = get_schedule(
                teacher.performer_profile.user_object,
                labels=[conference.conference_slug]).schedule_items
        ticket_items, role_items = get_checklist_items(
            teacher.performer_profile,
            conference,
            self.schedule)
        self.assertEqual(len(ticket_items), 1)
        self.assertEqual(len(role_items), 1)
        self.assertEqual(ticket_items[0]['ticket'],
                        transaction.ticket_item.title)
        self.assertEqual(role_items[self.role_condition.role],
                        [self.role_condition.checklistitem])

    def tearDown(self):
        self.role_condition.delete()
        self.ticket_condition.delete()
