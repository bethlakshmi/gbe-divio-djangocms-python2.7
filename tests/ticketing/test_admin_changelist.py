from django.test import (
    Client,
    TestCase
)
from django.contrib.auth.models import User
from tests.factories.ticketing_factories import(
    EventbriteSettingsFactory,
    NoEventRoleExclusionFactory,
    RoleEligibilityConditionFactory,
    RoleExclusionFactory,
    TicketingEligibilityConditionFactory,
    TicketingExclusionFactory,
    TicketItemFactory,
)
from tests.factories.gbe_factories import ConferenceFactory
from django.contrib.admin.sites import AdminSite
from tests.functions.gbe_functions import (
    login_as,
    make_act_app_purchase,
    make_vendor_app_purchase,
    setup_admin_w_privs,
)
from django.urls import reverse


class TicketingChangeListTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = setup_admin_w_privs([])

    def setUp(self):
        self.client = Client()
        login_as(self.privileged_user, self)

    def test_get_ticketitem_active(self):
        ticket = TicketItemFactory(live=True, has_coupon=False)
        response = self.client.get('/admin/ticketing/ticketitem/', follow=True)
        self.assertContains(response, "True")

    def test_get_ebsettings_active(self):
        settings = EventbriteSettingsFactory()
        response = self.client.get(
            '/admin/ticketing/eventbritesettings/',
            follow=True)
        self.assertContains(response, str(settings))

    def test_get_conference(self):
        ticket = TicketItemFactory()
        response = self.client.get('/admin/ticketing/ticketitem/', follow=True)
        self.assertContains(response, str(ticket.ticketing_event.conference))

    def test_get_transaction_act_fee_paid(self):
        conference = ConferenceFactory()
        transaction = make_act_app_purchase(conference, self.privileged_user)
        response = self.client.get('/admin/ticketing/transaction/',
                                   follow=True)
        self.assertContains(response,
                            transaction.ticket_item.ticketing_event.title)
        self.assertContains(response, transaction.ticket_item.title)
        self.assertContains(response,
                            transaction.purchaser.matched_to_user.username)

    def test_get_transaction_vendor_fee_paid(self):
        conference = ConferenceFactory()
        transaction = make_vendor_app_purchase(conference,
                                               self.privileged_user)
        response = self.client.get('/admin/ticketing/transaction/',
                                   follow=True)
        self.assertContains(response,
                            transaction.ticket_item.ticketing_event.title)
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
        self.assertContains(response, ticket.ticketing_event.title)
        self.assertContains(response, ticket.title)

    def test_get_role_eligibility(self):
        role_condition = RoleEligibilityConditionFactory()
        response = self.client.get(
            '/admin/ticketing/roleeligibilitycondition/',
            follow=True)
        self.assertContains(response, role_condition.role)
        self.assertContains(response, role_condition.checklistitem)

    def test_get_ticketing_eligibility_edit_ticket_exclude(self):
        ticket = TicketItemFactory()
        ticket2 = TicketItemFactory(ticketing_event__title=None)
        ticket3 = TicketItemFactory()
        match_condition = TicketingEligibilityConditionFactory(
            tickets=[ticket])
        exclusion = TicketingExclusionFactory(
            condition=match_condition,
            tickets=[ticket2, ticket3])
        response = self.client.get(
            reverse("admin:ticketing_ticketingeligibilitycondition_change",
                    args=(match_condition.id,)),
            follow=True)
        self.assertContains(response, "%s, %s" % (ticket2, ticket3))

    def test_get_ticketing_eligibility_cond_changelist(self):
        ticket = TicketItemFactory()
        ticket2 = TicketItemFactory()
        ticket3 = TicketItemFactory()
        match_condition = TicketingEligibilityConditionFactory(
            tickets=[ticket])
        exclusion = TicketingExclusionFactory(
            condition=match_condition,
            tickets=[ticket2, ticket3])
        response = self.client.get(
            reverse(
                "admin:ticketing_ticketingeligibilitycondition_changelist"),
            follow=True)
        self.assertContains(response,
                            match_condition.checklistitem.description)

    def test_get_ticketing_eligibility_edit_role_exclude(self):
        ticket = TicketItemFactory()
        match_condition = TicketingEligibilityConditionFactory(
            tickets=[ticket])
        exclusion = NoEventRoleExclusionFactory(
            condition=match_condition,
            role="Volunteer")
        response = self.client.get(
            reverse("admin:ticketing_ticketingeligibilitycondition_change",
                    args=(match_condition.id,)),
            follow=True)
        self.assertContains(response, "Volunteer")

    def test_get_ticketing_eligibility_edit_role_exclude_event(self):
        ticket = TicketItemFactory()
        match_condition = TicketingEligibilityConditionFactory(
            tickets=[ticket])
        exclusion = RoleExclusionFactory(
            condition=match_condition,
            role="Performer")
        response = self.client.get(
            reverse("admin:ticketing_ticketingeligibilitycondition_change",
                    args=(match_condition.id,)),
            follow=True)
        self.assertContains(response, "Performer in %s" % exclusion.event)
