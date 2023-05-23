from django.urls import reverse
from django.test import TestCase
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
)
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    TransactionFactory,
    TicketingExclusionFactory,
)
from tests.contexts import ShowContext
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as
)


class TestPerformerCompView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.priv_profile = ProfileFactory()
        grant_privilege(cls.priv_profile, 'Registrar')
        cls.url = reverse('perf_comp', urlconf='gbe.reporting.urls')

    def test_no_priv_fail(self):
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_empty_succeed(self):
        ConferenceFactory()
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Performer Comps")

    def test_old_conf_succeed(self):
        old_conf = ConferenceFactory(status="completed", accepting_bids=False)
        login_as(self.priv_profile, self)
        response = self.client.get(
            "%s?conf_slug=%s&submit=Select+conference" % (
                self.url,
                old_conf.conference_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Performer Comps")

    def test_performer_one_show(self):
        role_condition = RoleEligibilityConditionFactory(role="Performer")
        context = ShowContext()

        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            str(role_condition.checklistitem),
            msg_prefix="Role condition for performer was not found")
        self.assertContains(
            response,
            str(context.performer.contact),
            msg_prefix="Performer is not in the list")

    def test_performer_ticket_exception(self):
        role_condition = RoleEligibilityConditionFactory(role="Performer")
        other_role_condition = RoleEligibilityConditionFactory(
            role="Performer")
        context = ShowContext()
        transaction = TransactionFactory(
            purchaser__matched_to_user=context.performer.contact.user_object,
            ticket_item__ticketing_event__conference=context.conference)
        ticketingexclusion = TicketingExclusionFactory(
            condition=role_condition,
            tickets=[transaction.ticket_item])

        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            str(role_condition.checklistitem),
            msg_prefix="Role condition present despite exclusion")
        self.assertContains(
            response,
            str(other_role_condition.checklistitem),
            msg_prefix="Role condition with no exclusion was not found")
        self.assertContains(
            response,
            str(context.performer.contact),
            msg_prefix="Performer is not in the list")

    def test_performer_w_no_stuff_does_not_show(self):
        role_condition = RoleEligibilityConditionFactory(role="Performer")
        context = ShowContext()
        transaction = TransactionFactory(
            purchaser__matched_to_user=context.performer.contact.user_object,
            ticket_item__ticketing_event__conference=context.conference)
        ticketingexclusion = TicketingExclusionFactory(
            condition=role_condition,
            tickets=[transaction.ticket_item])

        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            str(role_condition.checklistitem),
            msg_prefix="Role condition present despite exclusion")
        self.assertNotContains(
            response,
            str(context.performer.contact),
            msg_prefix="Performer w no stuff shouldn't be here")
