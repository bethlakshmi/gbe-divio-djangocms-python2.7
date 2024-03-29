from django.urls import reverse
from django.test import TestCase
from tests.factories.gbe_factories import (
    BioFactory,
    ConferenceFactory,
    ProfileFactory,
)
from tests.factories.scheduler_factories import PeopleAllocationFactory
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    TransactionFactory,
    TicketingEligibilityConditionFactory
)
from tests.contexts import (
    ClassContext,
    VolunteerContext,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as
)
from tests.functions.scheduler_functions import get_or_create_profile
from tests.functions.ticketing_functions import set_form
from gbetext import unsigned_forms_message


class TestWelcomeLetter(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.priv_profile = ProfileFactory()
        grant_privilege(cls.priv_profile, 'Act Reviewers')
        cls.url = reverse('welcome_letter', urlconf='gbe.reporting.urls')

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
            str(context.teacher.contact),
            msg_prefix="Teacher is not in the list")

    def test_personal_schedule_teacher_booking(self):
        '''a teacher booked into a class, with an active role condition
           should have a booking.  Also includes unsigned form warning
        '''
        role_condition = RoleEligibilityConditionFactory()
        sign_condition = RoleEligibilityConditionFactory(
            role="Teacher",
            checklistitem__description="Landing page sign!",
            checklistitem__e_sign_this=set_form())
        context = ClassContext()

        login_as(self.priv_profile, self)
        response = self.client.get(
            self.url,
            data={"conf_slug": context.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            str(context.teacher.contact))
        self.assertContains(
            response,
            context.bid.b_title)
        self.assertContains(
            response,
            str(context.room))
        self.assertContains(response, "dedicated-sched")
        self.assertContains(response, unsigned_forms_message)

    def test_personal_schedule_volunteer_w_slug(self):
        '''a teacher booked into a class, with an active role condition
           should have a booking
        '''
        context = VolunteerContext()

        login_as(self.priv_profile, self)
        response = self.client.get(
            self.url,
            data={"conf_slug": context.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(context.profile))
        self.assertContains(response, "%s: %s" % (
            context.sched_event.title,
            context.opp_event.title))

    def test_personal_schedule_interest_booking(self):
        '''a teacher booked into a class, with an active role condition
           should have a booking
        '''
        role_condition = RoleEligibilityConditionFactory()
        context = ClassContext()
        profile = ProfileFactory()
        booking = PeopleAllocationFactory(
            people=get_or_create_profile(profile),
            role="Interested",
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
            context.bid.b_title,
            2)
        self.assertContains(response, "interested-sched")

    def test_ticket_purchase(self):
        '''a ticket purchaser gets a checklist item
        '''
        transaction = TransactionFactory()
        canceled_trans = TransactionFactory(
            ticket_item__ticketing_event__conference=transaction.
            ticket_item.ticketing_event.conference,
            purchaser=transaction.purchaser,
            status="canceled")
        purchaser = ProfileFactory(
            user_object=transaction.purchaser.matched_to_user)
        conference = transaction.ticket_item.ticketing_event.conference
        ticket_condition = TicketingEligibilityConditionFactory(
            tickets=[transaction.ticket_item]
        )
        other_ticket_condition = TicketingEligibilityConditionFactory(
            tickets=[canceled_trans.ticket_item]
        )
        context = ClassContext(
            conference=transaction.ticket_item.ticketing_event.conference)
        context.set_interest(interested_profile=purchaser)

        request = self.client.get(
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
        self.assertNotContains(
            response,
            str(other_ticket_condition.checklistitem))

    def test_personal_schedule_only_active(self):
        '''a teacher booked into a class, with an active role condition
           should have a booking
        '''
        role_condition = RoleEligibilityConditionFactory()
        teacher = BioFactory(contact__user_object__is_active=False)
        context = ClassContext(teacher=teacher)

        login_as(self.priv_profile, self)
        response = self.client.get(
            self.url,
            data={"conf_slug": context.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            str(teacher.contact))
        self.assertNotContains(
            response,
            context.bid.b_title)

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

        request = self.client.get(
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
