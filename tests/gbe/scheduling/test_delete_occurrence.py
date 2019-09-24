from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
)
from scheduler.models import EventItem
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts import (
    ClassContext,
    VolunteerContext
)
from gbe.models import (
    Class,
    Conference,
)
from scheduler.models import Event
from datetime import timedelta


class TestDeleteSchedule(TestCase):
    view_name = 'delete_occurrence'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        Conference.objects.all().delete()
        self.context = ClassContext()
        self.url = reverse(self.view_name,
                           urlconf="gbe.scheduling.urls",
                           args=[self.context.sched_event.pk])

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(
            'login',
            urlconf='gbe.urls') + "/?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_bad_event(self):
        login_as(self.privileged_profile, self)
        bad_url = reverse(self.view_name,
                          urlconf="gbe.scheduling.urls",
                          args=[self.context.sched_event.pk+1])
        response = self.client.get(bad_url, follow=True)
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+1))
        self.assertRedirects(response,
                             reverse('manage_event_list',
                                     urlconf='gbe.scheduling.urls'))

    def test_good_user_get_success_redirect(self):
        login_as(self.privileged_profile, self)
        redirect_to = "%s?%s-day=%d" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]),
            self.context.conference.conference_slug,
            self.context.days[0].pk)
        response = self.client.get(
            "%s?next=%s" % (self.url, redirect_to),
            follow=True)
        self.assertRedirects(response,
                             redirect_to)
        self.assertNotContains(
            response,
            '<td class="bid-table">%s</td>' % self.context.bid.e_title)
        self.assertContains(response, "This event has been deleted.")
        check_class = Class.objects.get(pk=self.context.bid.pk)
        self.assertFalse(check_class.visible)

    def test_good_user_get_success_keep_gbe_event(self):
        second_class = self.context.schedule_instance(
            starttime=self.context.sched_event.starttime + timedelta(hours=1))
        login_as(self.privileged_profile, self)
        redirect_to = "%s?%s-day=%d" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]),
            self.context.conference.conference_slug,
            self.context.days[0].pk)
        response = self.client.get(
            "%s?next=%s" % (self.url, redirect_to),
            follow=True)
        self.assertContains(
            response,
            '<td class="bid-table">%s</td>' % self.context.bid.e_title)
        self.assertContains(response, "This event has been deleted.")
        self.assertTrue(Event.objects.filter(pk=second_class.pk).exists())
        check_class = Class.objects.get(pk=self.context.bid.pk)
        self.assertTrue(check_class.visible)

    def test_delete_w_parent(self):
        vol_context = VolunteerContext()
        self.url = reverse(self.view_name,
                           urlconf="gbe.scheduling.urls",
                           args=[vol_context.sched_event.pk])
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, "PARENT_EVENT_DELETION")
