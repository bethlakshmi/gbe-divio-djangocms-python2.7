from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceFactory,
    ConferenceDayFactory,
    ProfileFactory,
    RoomFactory,
)
from scheduler.models import Event
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    login_as,
)
from gbe_forms_text import event_type_options
from tests.functions.gbe_scheduling_functions import (
    assert_event_was_picked_in_wizard,
    assert_good_sched_event_form_wizard,
)
from datetime import (
    datetime,
    timedelta,
)
from settings import (
    GBE_DATE_FORMAT,
    GBE_DATETIME_FORMAT,
)
from tests.contexts import (
    ClassContext,
    ShowContext,
    VolunteerContext,
)
from gbe_forms_text import (
    copy_mode_labels,
    copy_mode_choices,
)
from string import replace


class TestCopyOccurrence(TestCase):
    view_name = 'copy_event_schedule'
    copy_date_format = "%a, %b %-d, %Y %-I:%M %p"

    def setUp(self):
        self.context = VolunteerContext()
        self.url = reverse(
            self.view_name,
            args=[self.context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def assert_good_mode_form(self, response, title, date):
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            self.context.conf_day.day.strftime(GBE_DATE_FORMAT))
        self.assertContains(response, copy_mode_choices[0][1])
        self.assertContains(response, copy_mode_choices[1][1])
        self.assertContains(response, "%s - %s" % (
            title,
            date.strftime(GBE_DATETIME_FORMAT)))

    def test_create_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Copying - %s: %s" % (
            self.context.event.e_title,
            self.context.sched_event.starttime.strftime(
                self.copy_date_format)))

    def test_authorized_user_get_no_child_event(self):
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.opp_event.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            self.context.conf_day.day.strftime(GBE_DATE_FORMAT))
        self.assertNotContains(response, copy_mode_choices[0][1])

    def test_authorized_user_get_w_child_events(self):
        target_event = VolunteerContext()
        self.context.add_opportunity()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_good_mode_form(
            response,
            target_event.event.e_title,
            target_event.sched_event.start_time)

    def test_bad_occurrence(self):
        url = reverse(
            self.view_name,
            args=[self.context.sched_event.pk+100],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_authorized_user_get_show(self):
        show_context = VolunteerContext()
        target_context = ShowContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assert_good_mode_form(
            response,
            target_context.show.e_title,
            target_context.sched_event.start_time)

    def test_authorized_user_get_class(self):
        copy_class = ClassFactory()
        vol_context = VolunteerContext(event=copy_class)
        target_context = ClassContext()
        url = reverse(
            self.view_name,
            args=[vol_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assert_good_mode_form(
            response,
            target_context.bid.e_title,
            target_context.sched_event.start_time)

    def test_copy_single_event(self):
        another_day = ConferenceDayFactory(
            conference=self.context.conference,
            day=self.context.conf_day.day + timedelta(days=1))
        data = {
            'copy_to_day': another_day.pk,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.opp_event.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.post(self.url, data=data, follow=True)
        max_pk = Event.objects.latest('pk').pk
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[another_day.conference.conference_slug]),
            another_day.conference.conference_slug,
            another_day.pk,
            str([max_pk]),)
        self.assertRedirects(response, redirect_url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s' % (
                self.context.opportunity.e_title,
                datetime.combine(
                    another_day.day,
                    self.context.opp_event.starttime.time()).strftime(
                    GBE_DATETIME_FORMAT)))

    def test_authorized_user_pick_mode_include_parent(self):
        another_day = ConferenceDayFactory(conference=self.context.conference)
        show_context = VolunteerContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk,
            'pick_mode': "Next",
        }
        delta = another_day.day - show_context.sched_event.starttime.date()
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            '<input checked="checked" id="id_copy_mode_1" name="copy_mode" ' +
            'type="radio" value="include_parent" />')
        self.assertContains(
            response,
            '<option value="%d" selected="selected">' % another_day.pk)
        self.assertContains(response, "Choose Sub-Events to be copied")
        self.assertContains(response, "%s - %s" % (
            show_context.opportunity.e_title,
            (show_context.opp_event.start_time + delta).strftime(
                        self.copy_date_format)))

    def test_authorized_user_pick_mode_bad_input(self):
        another_day = ConferenceDayFactory(conference=self.context.conference)
        show_context = VolunteerContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk + 100,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice.')

    def test_authorized_user_pick_mode_no_day(self):
        show_context = VolunteerContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'include_parent',
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            'Must choose a day when copying all events.')

    def test_authorized_user_pick_mode_no_event(self):
        show_context = VolunteerContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'copy_children_only',
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            'Must choose the target event when copying sub-events.')

    def test_authorized_user_pick_mode_only_children(self):
        show_context = VolunteerContext()
        target_context = ShowContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'copy_children_only',
            'target_event': target_context.sched_event.pk,
            'pick_mode': "Next",
        }
        delta = target_context.sched_event.starttime.date(
            ) - show_context.sched_event.starttime.date()
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            '<input checked="checked" id="id_copy_mode_0" name="copy_mode" ' +
            'type="radio" value="copy_children_only" />')
        self.assertContains(
            response,
            '<option value="%d" selected="selected">' % (
                target_context.sched_event.pk))
        self.assertContains(response, "Choose Sub-Events to be copied")
        self.assertContains(response, "%s - %s" % (
            show_context.opportunity.e_title,
            (show_context.opp_event.start_time + delta).strftime(
                        self.copy_date_format)))

    def test_copy_child_event(self):
        show_context = VolunteerContext()
        target_context = ShowContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'copy_children_only',
            'target_event': target_context.sched_event.pk,
            'copied_event': show_context.opp_event.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        max_pk = Event.objects.latest('pk').pk
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[target_context.conference.conference_slug]),
            target_context.conference.conference_slug,
            target_context.days[0].pk,
            str([max_pk]),)
        self.assertRedirects(response, redirect_url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s' % (
                show_context.opportunity.e_title,
                datetime.combine(
                    target_context.days[0].day,
                    show_context.opp_event.starttime.time()).strftime(
                    GBE_DATETIME_FORMAT)))

    def test_copy_child_parent_events(self):
        another_day = ConferenceDayFactory()
        show_context = VolunteerContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk,
            'copied_event': show_context.opp_event.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        max_pk = Event.objects.latest('pk').pk
        response = self.client.post(url, data=data, follow=True)
        new_occurrences = []
        for occurrence in Event.objects.filter(pk__gt=max_pk):
            new_occurrences += [occurrence.pk]
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[another_day.conference.conference_slug]),
            another_day.conference.conference_slug,
            another_day.pk,
            replace(str(new_occurrences), " ", "%20"))
        self.assertRedirects(response, redirect_url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s' % (
                show_context.opportunity.e_title,
                datetime.combine(
                    another_day.day,
                    show_context.opp_event.starttime.time()).strftime(
                    GBE_DATETIME_FORMAT)))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s' % (
                show_context.event.e_title,
                datetime.combine(
                    another_day.day,
                    show_context.sched_event.starttime.time()).strftime(
                    GBE_DATETIME_FORMAT)))

    def test_copy_child_not_like_parent(self):
        another_day = ConferenceDayFactory()
        show_context = VolunteerContext()
        opportunity, opp_sched = show_context.add_opportunity(
            start_time=show_context.sched_event.starttime + timedelta(1.3))
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk,
            'copied_event': opp_sched.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        max_pk = Event.objects.latest('pk').pk
        response = self.client.post(url, data=data, follow=True)
        new_occurrences = []
        for occurrence in Event.objects.filter(pk__gt=max_pk):
            new_occurrences += [occurrence.pk]
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[another_day.conference.conference_slug]),
            another_day.conference.conference_slug,
            another_day.pk,
            replace(str(new_occurrences), " ", "%20"))
        self.assertRedirects(response, redirect_url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s' % (
                opportunity.e_title,
                datetime.combine(
                    another_day.day + timedelta(1),
                    opp_sched.starttime.time()).strftime(
                    GBE_DATETIME_FORMAT)))
        new_vol_opp = Event.objects.get(pk=max_pk)
        self.assertEqual(new_vol_opp.max_volunteer, opp_sched.max_volunteer)
        self.assertEqual(new_vol_opp.location, opp_sched.location)

    def test_copy_only_parent_event(self):
        another_day = ConferenceDayFactory()
        show_context = VolunteerContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        max_pk = Event.objects.latest('pk').pk
        redirect_url = "%s?%s-day=%d&filter=Filter&new=[%s]" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[another_day.conference.conference_slug]),
            another_day.conference.conference_slug,
            another_day.pk,
            str(max_pk),)
        self.assertRedirects(response, redirect_url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s' % (
                show_context.event.e_title,
                datetime.combine(
                    another_day.day,
                    show_context.sched_event.starttime.time()).strftime(
                    GBE_DATETIME_FORMAT)))
        self.assertContains(response, "Occurrence has been updated.<br>", 1)

    def test_copy_bad_second_form(self):
        another_day = ConferenceDayFactory()
        show_context = VolunteerContext()
        url = reverse(self.view_name,
                      args=[show_context.sched_event.pk],
                      urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk,
            'copied_event': "bad",
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response,
                            "bad is not one of the available choices.")
