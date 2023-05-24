from django.urls import reverse
from django.test import TestCase, Client
from gbe.models import Conference
from tests.factories.gbe_factories import ProfileFactory
from tests.contexts import (
    ActTechInfoContext,
    ClassContext,
    PurchasedTicketContext,
    StaffAreaContext,
    VolunteerContext
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestReports(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfileFactory()
        grant_privilege(cls.profile, 'Registrar')
        cls.ticket_context = PurchasedTicketContext()

    def test_env_stuff_fail(self):
        '''env_stuff view should load for privileged users
           and fail for others
        '''
        bad_profile = ProfileFactory()
        login_as(bad_profile, self)
        response = self.client.get(
            reverse('env_stuff',
                    urlconf="gbe.reporting.urls"))
        self.assertEqual(response.status_code, 403)

    def test_env_stuff_succeed(self):
        '''env_stuff view should load with no conf choice
        '''
        transaction = self.ticket_context.transaction
        login_as(self.profile, self)
        response = self.client.get(
            reverse('env_stuff',
                    urlconf="gbe.reporting.urls"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=env_stuff.csv")
        self.assertContains(
            response,
            "Badge Name,First,Last,Tickets,Personae," +
            "Staff Lead,Volunteering,Presenter,Show")
        self.assertContains(
            response,
            transaction.purchaser.matched_to_user.first_name)
        self.assertContains(
            response,
            transaction.ticket_item.title)

    def test_env_stuff_w_inactive_purchaser(self):
        '''env_stuff view should load with no conf choice
        '''
        Conference.objects.all().delete()
        inactive = ProfileFactory(
            display_name="DON'T SEE THIS",
            user_object__is_active=False
        )
        ticket_context = PurchasedTicketContext(profile=inactive)
        transaction = ticket_context.transaction
        login_as(self.profile, self)
        response = self.client.get(
            reverse('env_stuff',
                    urlconf="gbe.reporting.urls"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=env_stuff.csv")
        self.assertContains(
            response,
            "Badge Name,First,Last,Tickets,Personae," +
            "Staff Lead,Volunteering,Presenter,Show")
        self.assertNotContains(
            response,
            inactive.display_name)

    def test_env_stuff_succeed_w_conf(self):
        '''env_stuff view should load for a selected conference slug
        '''
        t = self.ticket_context.transaction
        login_as(self.profile, self)
        response = self.client.get(reverse(
            'env_stuff',
            urlconf="gbe.reporting.urls",
            args=[
                t.ticket_item.ticketing_event.conference.conference_slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=env_stuff.csv")
        self.assertContains(
            response,
            "Badge Name,First,Last,Tickets,Personae," +
            "Staff Lead,Volunteering,Presenter,Show")
        self.assertContains(
            response,
            t.purchaser.matched_to_user.first_name)
        self.assertContains(
            response,
            t.ticket_item.title)

    def test_env_stuff_succeed_w_performer(self):
        '''env_stuff view should load with no conf choice
        '''
        context = ActTechInfoContext(conference=self.ticket_context.conference)
        login_as(self.profile, self)
        response = self.client.get(
            reverse('env_stuff',
                    urlconf="gbe.reporting.urls"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=env_stuff.csv")
        self.assertContains(
            response,
            "Badge Name,First,Last,Tickets,Personae," +
            "Staff Lead,Volunteering,Presenter,Show")
        self.assertContains(
            response,
            context.performer)
        self.assertContains(
            response,
            context.sched_event.title)

    def test_env_stuff_succeed_w_teacher(self):
        '''env_stuff view should load with no conf choice
        '''
        context = ClassContext(conference=self.ticket_context.conference)
        login_as(self.profile, self)
        response = self.client.get(
            reverse('env_stuff',
                    urlconf="gbe.reporting.urls"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=env_stuff.csv")
        self.assertContains(
            response,
            "Badge Name,First,Last,Tickets,Personae," +
            "Staff Lead,Volunteering,Presenter,Show")
        self.assertContains(
            response,
            context.teacher)
        self.assertContains(
            response,
            context.sched_event.title)

    def test_env_stuff_succeed_w_volunteer(self):
        '''env_stuff view should load with no conf choice
        '''
        context = VolunteerContext(conference=self.ticket_context.conference)
        staff_lead = context.set_staff_lead()
        login_as(self.profile, self)
        response = self.client.get(
            reverse('env_stuff',
                    urlconf="gbe.reporting.urls"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Disposition'),
                         "attachment; filename=env_stuff.csv")
        self.assertContains(
            response,
            "Badge Name,First,Last,Tickets,Personae," +
            "Staff Lead,Volunteering,Presenter,Show")
        self.assertContains(
            response,
            context.profile)
        self.assertContains(
            response,
            staff_lead)
        self.assertContains(
            response,
            context.opp_event.title)
        self.assertContains(
            response,
            context.sched_event.title)
