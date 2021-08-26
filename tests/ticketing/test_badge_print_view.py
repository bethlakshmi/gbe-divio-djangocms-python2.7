from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.contexts import (
    ClassContext,
    PurchasedTicketContext,
)
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    TicketingEligibilityConditionFactory,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestBadgePrintView(TestCase):
    view_name = 'badge_print'

    def setUp(self):
        self.client = Client()
        self.privileged_user = ProfileFactory.create().user_object
        grant_privilege(self.privileged_user,
                        'Registrar',
                        'view_transaction')
        self.url = reverse(self.view_name, urlconf='ticketing.urls')
        self.class_context = ClassContext()
        self.ticket_context = PurchasedTicketContext(
            profile=self.class_context.teacher.performer_profile,
            conference=self.class_context.conference)

    def test_w_ticket_condition(self):
        '''loads with the default conference selection.
        '''
        ticket_condition = TicketingEligibilityConditionFactory(
            checklistitem__badge_title="Badge Name")
        ticket_condition.tickets.add(
            self.ticket_context.transaction.ticket_item)
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=print_badges.csv")
        self.assertContains(
            response,
            "First,Last,username,Badge Name,Badge Type,Ticket Purchased,Date")
        self.assertContains(
            response,
            self.ticket_context.profile.user_object.username)
        self.assertContains(
            response,
            self.ticket_context.transaction.ticket_item.title)
        self.assertContains(response, "Badge Name")

    def test_w_role_condition(self):
        '''loads with the default conference selection.
        '''
        role_condition = RoleEligibilityConditionFactory(
            checklistitem__badge_title="Other Badge Name",
            role="Teacher")
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            self.class_context.teacher.performer_profile.user_object.username)
        self.assertContains(
            response,
            "Role Condition: Teacher")
        self.assertContains(response, "Other Badge Name")

    def test_there_can_be_only_one(self):
        ticket_condition = TicketingEligibilityConditionFactory(
            checklistitem__badge_title="Badge Name")
        ticket_condition.tickets.add(
            self.ticket_context.transaction.ticket_item)
        role_condition = RoleEligibilityConditionFactory(
            checklistitem__badge_title="Other Badge Name",
            role="Teacher")
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            self.ticket_context.profile.get_badge_name(),
            1)
        self.assertContains(
            response,
            self.ticket_context.transaction.ticket_item.title)
        self.assertContains(response, "Badge Name")
        self.assertNotContains(
            response,
            "Role Condition: Teacher")
        self.assertNotContains(response, "Other Badge Name")

    def tearDown(self):
        self.class_context.sched_event.delete()
        self.ticket_context.transaction.purchaser.delete()
        self.ticket_context.transaction.delete()
        self.ticket_context.profile.user_object.delete()
        self.ticket_context.conference.delete()
