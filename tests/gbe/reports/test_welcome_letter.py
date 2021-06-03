from django.urls import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.factories.scheduler_factories import (
    ResourceAllocationFactory,
    WorkerFactory,
)
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    TransactionFactory,
    TicketingEligibilityConditionFactory
)
from tests.contexts import ClassContext
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as
)


class TestWelcomeLetter(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.priv_profile = ProfileFactory()
        grant_privilege(self.priv_profile, 'Act Reviewers')
        self.url = reverse('welcome_letter', urlconf='gbe.reporting.urls')

    def test_personal_schedule_fail(self):
        '''personal_schedule view should load for privileged users
           and fail for others
        '''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_personal_schedule_succeed(self):
        '''personal_schedule view should load for privileged users
           and fail for others
        '''
        ConferenceFactory()
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_personal_schedule_teacher_checklist(self):
        '''a teacher booked into a class, with an active role condition
           should get a checklist item
        '''
        role_condition = RoleEligibilityConditionFactory()
        context = ClassContext()

        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            str(role_condition.checklistitem),
            msg_prefix="Role condition for teacher was not found")
        self.assertContains(
            response,
            str(context.teacher.performer_profile),
            msg_prefix="Teacher is not in the list")

    def test_personal_schedule_teacher_booking(self):
        '''a teacher booked into a class, with an active role condition
           should have a booking
        '''
        role_condition = RoleEligibilityConditionFactory()
        context = ClassContext()

        login_as(self.priv_profile, self)
        response = self.client.get(
            self.url,
            data={"conf_slug": context.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            str(context.teacher.performer_profile))
        self.assertContains(
            response,
            context.bid.e_title)
        self.assertContains(
            response,
            str(context.room))
        self.assertContains(response, "dedicated-sched")

    def test_personal_schedule_interest_booking(self):
        '''a teacher booked into a class, with an active role condition
           should have a booking
        '''
        role_condition = RoleEligibilityConditionFactory()
        context = ClassContext()
        profile = ProfileFactory()
        booking = ResourceAllocationFactory(
            resource=WorkerFactory(
                _item=profile,
                role="Interested"),
            event=context.sched_event)

        login_as(self.priv_profile, self)
        response = self.client.get(
            self.url,
            data={"conf_slug": context.conference.conference_slug})
        self.assertContains(
            response,
            str(profile))
        self.assertContains(
            response,
            context.bid.e_title,
            2)
        self.assertContains(response, "interested-sched")

    def test_ticket_purchase(self):
        '''a ticket purchaser gets a checklist item
        '''
        transaction = TransactionFactory()
        purchaser = ProfileFactory(
            user_object=transaction.purchaser.matched_to_user)
        conference = transaction.ticket_item.ticketing_event.conference
        ticket_condition = TicketingEligibilityConditionFactory(
            tickets=[transaction.ticket_item]
        )
        context = ClassContext(
            conference=transaction.ticket_item.ticketing_event.conference)
        context.set_interest(interested_profile=purchaser)

        request = self.factory.get(
            'reports/schedule_all?conf_slug='+conference.conference_slug)
        login_as(self.priv_profile, self)
        response = self.client.get(
            self.url,
            data={"conf_slug": conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            str(purchaser),
            msg_prefix="Buyer is not in the list")
        self.assertContains(
            response,
            str(ticket_condition.checklistitem))

    def test_personal_schedule_only_active(self):
        '''a teacher booked into a class, with an active role condition
           should have a booking
        '''
        role_condition = RoleEligibilityConditionFactory()
        teacher = PersonaFactory(contact__user_object__is_active=False)
        context = ClassContext(teacher=teacher)

        login_as(self.priv_profile, self)
        response = self.client.get(
            self.url,
            data={"conf_slug": context.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            str(teacher.performer_profile))
        self.assertNotContains(
            response,
            context.bid.e_title)

    def test_ticket_purchase_solo_profile(self):
        '''a ticket purchaser gets a checklist item
        '''
        transaction = TransactionFactory()
        purchaser = ProfileFactory(
            user_object=transaction.purchaser.matched_to_user)
        conference = transaction.ticket_item.ticketing_event.conference
        ticket_condition = TicketingEligibilityConditionFactory(
            tickets=[transaction.ticket_item]
        )

        request = self.factory.get(
            'reports/schedule_all?conf_slug='+conference.conference_slug)
        login_as(self.priv_profile, self)
        response = self.client.get(
            reverse('welcome_letter',
                    urlconf='gbe.reporting.urls',
                    args=[purchaser.pk]),
            data={"conf_slug": conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            str(purchaser),
            msg_prefix="Buyer is not in the list")
        self.assertContains(
            response,
            str(ticket_condition.checklistitem))
