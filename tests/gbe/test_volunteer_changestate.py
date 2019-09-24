import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    EmailTemplateSenderFactory,
    VolunteerFactory,
    ProfilePreferencesFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_email_template_create,
    assert_email_template_used,
    grant_privilege,
    login_as,
)
from django.core.exceptions import PermissionDenied
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from gbe.models import Conference
from gbe.functions import get_current_conference
from gbetext import bidder_email_fail_msg
from datetime import timedelta


class TestVolunteerChangestate(TestCase):
    '''Tests for volunteer_changestate view'''
    view_name = 'volunteer_changestate'

    def setUp(self):
        Conference.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.volunteer = VolunteerFactory(submitted=True)
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        grant_privilege(self.privileged_user, 'Volunteer Reviewers')

    def test_volunteer_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data={'accepted': 3})
        nt.assert_equal(response.status_code, 302)

    def test_volunteer_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.post(url)
        nt.assert_equal(response.status_code, 403)

    def test_volunteer_changestate_authorized_user_post(self):
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'e_conference': self.volunteer.b_conference,
                'events': [],
                'accepted': 3}
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 302)

    def test_volunteer_accept_sends_notification_makes_template(self):
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'e_conference': self.volunteer.b_conference,
                'events': [],
                'accepted': 3}
        response = self.client.post(url, data=data)
        assert_email_template_create(
            'volunteer schedule update',
            "A change has been made to your Volunteer Schedule!"
        )

    def test_volunteer_accept_sends_notification_has_template(self):
        EmailTemplateSenderFactory(
            from_email="volunteeremail@notify.com",
            template__name='volunteer schedule update',
            template__subject="test template"
        )
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': self.volunteer.b_conference,
                'events': [],
                'accepted': 3}
        response = self.client.post(url, data=data)
        assert_email_template_used(
            "test template", "volunteeremail@notify.com")

    def test_volunteer_accept_sends_notification_fail(self):
        ProfilePreferencesFactory(profile=self.volunteer.profile)
        EmailTemplateSenderFactory(
            from_email="volunteeremail@notify.com",
            template__name='volunteer schedule update',
            template__subject="test template {% url 'gbehome' %}"
        )
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': self.volunteer.b_conference,
                'events': [],
                'accepted': 3}
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response,
                            bidder_email_fail_msg)

    def test_volunteer_withdraw_sends_notification_fail(self):
        ProfilePreferencesFactory(profile=self.volunteer.profile)
        EmailTemplateSenderFactory(
            from_email="volunteeremail@notify.com",
            template__name='volunteer withdrawn',
            template__subject="test template {% url 'gbehome' %}"
        )
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': self.volunteer.b_conference,
                'events': [],
                'accepted': 4}
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response,
                            bidder_email_fail_msg)

    def test_volunteer_withdraw_sends_notification(self):
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': self.volunteer.b_conference,
                'events': [],
                'accepted': 4}
        response = self.client.post(url, data=data)
        assert_email_template_used(
            "Your volunteer proposal has changed status to Withdrawn")

    def test_volunteer_changestate_gives_overbook_warning(self):
        ProfilePreferencesFactory(profile=self.volunteer.profile)
        context = VolunteerContext(
            profile=self.volunteer.profile)
        x, opp = context.add_opportunity()
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': context.conference,
                'events': [opp.pk],
                'accepted': 3}
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response, "SCHEDULE_CONFLICT")

    def test_volunteer_changestate_gives_overbook_warning_more(self):
        ProfilePreferencesFactory(profile=self.volunteer.profile)
        context = VolunteerContext(
            profile=self.volunteer.profile)
        x, opp = context.add_opportunity()
        opp.starttime = context.sched_event.starttime + timedelta(minutes=30)
        opp.save()
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': context.conference,
                'events': [opp.pk],
                'accepted': 3}
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response, "SCHEDULE_CONFLICT")

    def test_volunteer_changestate_gives_overbook_warning_always(self):
        ProfilePreferencesFactory(profile=self.volunteer.profile)
        context = VolunteerContext(
            profile=self.volunteer.profile)
        x, opp = context.add_opportunity()
        opp.starttime = context.sched_event.starttime - timedelta(minutes=30)
        opp.save()
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': context.conference,
                'events': [opp.pk],
                'accepted': 3}
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response, "SCHEDULE_CONFLICT")

    def test_volunteer_changestate_gives_event_over_full_warning(self):
        ProfilePreferencesFactory(profile=self.volunteer.profile)
        context = StaffAreaContext(
            conference=self.volunteer.b_conference,
        )
        opp = context.add_volunteer_opp()
        context.book_volunteer(
            volunteer_sched_event=opp,
            volunteer=context.staff_lead)
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': self.volunteer.b_conference,
                'events': [opp.pk],
                'accepted': 3}
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response, "OCCURRENCE_OVERBOOKED")
