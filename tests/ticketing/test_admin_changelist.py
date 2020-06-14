from django.test import (
    Client,
    TestCase
)
from django.contrib.auth.models import User
from tests.factories.ticketing_factories import(
    RoleEligibilityConditionFactory,
    TicketingEligibilityConditionFactory,
    TicketItemFactory,
)
from tests.factories.gbe_factories import ConferenceFactory
from django.contrib.admin.sites import AdminSite
from tests.functions.gbe_functions import (
    make_act_app_purchase,
    make_vendor_app_purchase,
)


class TicketingChangeListTests(TestCase):
    def setUp(self):
        self.client = Client()
        password = 'mypassword'
        self.privileged_user = User.objects.create_superuser(
            'myuser', 'myemail@test.com', password)
        self.client.login(
            username=self.privileged_user.username,
            password=password)

    def test_get_ticketitem_active(self):
        ticket = TicketItemFactory(live=True, has_coupon=False)
        response = self.client.get('/admin/ticketing/ticketitem/', follow=True)
        self.assertContains(response, "True")

    def test_get_eventcontainer_conference(self):
        ticket = TicketItemFactory()
        response = self.client.get('/admin/ticketing/ticketitem/', follow=True)
        self.assertContains(response, str(ticket.bpt_event.conference))

    def test_get_transaction_act_fee_paid(self):
        conference = ConferenceFactory()
        transaction = make_act_app_purchase(conference, self.privileged_user)
        response = self.client.get('/admin/ticketing/transaction/',
                                   follow=True)
        self.assertContains(response, transaction.ticket_item.ticket_id)
        self.assertContains(response, transaction.ticket_item.title)
        self.assertContains(response,
                            transaction.purchaser.matched_to_user.username)

    def test_get_transaction_vendor_fee_paid(self):
        conference = ConferenceFactory()
        transaction = make_vendor_app_purchase(conference, self.privileged_user)
        response = self.client.get('/admin/ticketing/transaction/',
                                   follow=True)
        self.assertContains(response, transaction.ticket_item.ticket_id)
        self.assertContains(response, transaction.ticket_item.title)
        self.assertContains(response,
                            transaction.purchaser.matched_to_user.username)

    def test_get_ticketing_eligibility(self):
        ticket = TicketItemFactory()
        match_condition = TicketingEligibilityConditionFactory(
            tickets=[ticket])
        response = self.client.get(
            '/admin/ticketing/ticketingeligibilitycondition/',
            follow=True)
        self.assertContains(response, ticket.ticket_id)
        self.assertContains(response, ticket.title)

    def test_get_role_eligibility(self):
        role_condition = RoleEligibilityConditionFactory()
        response = self.client.get(
            '/admin/ticketing/roleeligibilitycondition/',
            follow=True)
        self.assertContains(response, role_condition.role)
        self.assertContains(response, role_condition.checklistitem)
