from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceFactory,
    ConferenceDayFactory,
    GenericEventFactory,
    ProfileFactory,
    RoomFactory,
)
from scheduler.models import Event
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    grant_privilege,
    login_as,
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
    copy_errors,
)
from tests.gbe.test_gbe import TestGBE


class TestCopyOccurrence(TestGBE):
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
        self.assertContains(
            response,
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
        self.assertContains(
            response,
            self.context.conf_day.day.strftime(GBE_DATE_FORMAT))
        self.assertNotContains(response, copy_mode_choices[0][1])

    def test_authorized_user_get_right_rooms(self):
        not_this_room = RoomFactory()
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.opp_event.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.context.conf_day.day.strftime(GBE_DATE_FORMAT))
        self.assertNotContains(response, not_this_room.name)
        assert_option_state(
            response,
            self.context.room.pk,
            self.context.room.name,
            True)

    def test_authorized_user_get_w_child_events(self):
        target_event = VolunteerContext()
        self.context.add_opportunity()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_good_mode_form(
            response,
            target_event.event.e_title,
            target_event.sched_event.start_time)
        assert_option_state(
            response,
            target_event.room.pk,
            target_event.room.name)

    def test_authorized_user_get_w_child_events_special(self):
        original_event = GenericEventFactory(type='Special')
        target_event = GenericEventFactory(type='Special')
        target_context = VolunteerContext(event=target_event)
        original_context = VolunteerContext(event=original_event)
        original_context.add_opportunity()
        url = reverse(
            self.view_name,
            args=[original_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assert_good_mode_form(
            response,
            target_context.event.e_title,
            target_context.sched_event.start_time)
        assert_option_state(
            response,
            target_context.room.pk,
            target_context.room.name)
        self.assertContains(response, target_event.e_title)

    def test_bad_occurrence(self):
        url = reverse(
            self.view_name,
            args=[self.context.sched_event.pk+100],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
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
        #  copying ONLY volunteer events is OK, but copying the class is not
        self.assertEqual(403, response.status_code)

    def test_copy_single_event(self):
        another_day = ConferenceDayFactory(
            conference=self.context.conference,
            day=self.context.conf_day.day + timedelta(days=1))
        other_room = RoomFactory()
        other_room.conferences.add(another_day.conference)
        data = {
            'copy_to_day': another_day.pk,
            'room': other_room.pk,
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
        self.assertContains(response, other_room.name)
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

    def test_copy_single_event_room_conf_mismatch(self):
        another_day = ConferenceDayFactory(
            day=self.context.conf_day.day + timedelta(days=1))
        data = {
            'copy_to_day': another_day.pk,
            'room': self.context.room.pk,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.opp_event.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(response, copy_errors['room_conf_mismatch'])

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
            'room': self.context.room.pk,
            'pick_mode': "Next",
        }
        delta = another_day.day - show_context.sched_event.starttime.date()
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            '<input type="radio" name="copy_mode" value="include_parent" ' +
            'id="id_copy_mode_1" required checked />',
            html=True)
        self.assertContains(
            response,
            '<input type="radio" name="copy_mode" value="include_parent" ' +
            'id="id_copy_mode_1" required checked />',
            html=True)
        self.assertContains(
            response,
            '<option value="%d" selected>' % another_day.pk)
        self.assert_hidden_value(
            response,
            "id_room",
            "room",
            self.context.room.pk)
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
            'room': self.context.room.pk,
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
            'room': self.context.room.pk,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            copy_errors['no_day'])

    def test_authorized_user_pick_mode_no_event(self):
        show_context = VolunteerContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'copy_children_only',
            'room': self.context.room.pk,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            copy_errors['no_target'])

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
            'room': target_context.room.pk,
            'pick_mode': "Next",
        }
        delta = target_context.sched_event.starttime.date(
            ) - show_context.sched_event.starttime.date()
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(
            response,
            '<input type="radio" name="copy_mode" ' +
            'value="copy_children_only" ' +
            'id="id_copy_mode_0" required checked />',
            html=True)
        self.assertContains(
            response,
            '<option value="%d" selected>' % (
                target_context.sched_event.pk))
        self.assertContains(response, "Choose Sub-Events to be copied")
        self.assertContains(response, "%s - %s" % (
            show_context.opportunity.e_title,
            (show_context.opp_event.start_time + delta).strftime(
                        self.copy_date_format)))

    def test_authorized_user_pick_mode_parent_room_mismatch(self):
        show_context = VolunteerContext()
        target_context = ShowContext()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'copy_children_only',
            'target_event': target_context.sched_event.pk,
            'room': self.context.room.pk,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response, copy_errors['room_target_mismatch'])

    def test_copy_child_event_preserve_room(self):
        show_context = VolunteerContext()
        target_context = ShowContext(room=show_context.room)
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'copy_children_only',
            'target_event': target_context.sched_event.pk,
            'copied_event': show_context.opp_event.pk,
            'room': self.context.room.pk,
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
        self.assertContains(response, show_context.room.name)
        self.assertNotContains(response, self.context.room.name)
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

    def test_copy_child_change_room(self):
        show_context = VolunteerContext()
        target_context = ShowContext()
        show_context.conference.status_code = 'completed'
        show_context.conference.save()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'copy_children_only',
            'target_event': target_context.sched_event.pk,
            'copied_event': show_context.opp_event.pk,
            'room': target_context.room.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response, target_context.room.name, 2)
        self.assertNotContains(response, show_context.room.name)

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
            'room': self.context.room.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        max_pk = Event.objects.latest('pk').pk
        response = self.client.post(url, data=data, follow=True)
        new_occurrences = []
        for occurrence in Event.objects.filter(pk__gt=max_pk).order_by('pk'):
            new_occurrences += [occurrence.pk]
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[another_day.conference.conference_slug]),
            another_day.conference.conference_slug,
            another_day.pk,
            str(new_occurrences).replace(" ", "%20"))
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
        self.assertNotContains(response, "approval_needed")

    def test_copy_child_not_like_parent(self):
        another_day = ConferenceDayFactory()
        show_context = VolunteerContext()
        opportunity, opp_sched = show_context.add_opportunity(
            start_time=show_context.sched_event.starttime + timedelta(1.3))
        opp_sched.approval_needed = True
        opp_sched.save()
        url = reverse(
            self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk,
            'copied_event': opp_sched.pk,
            'room': self.context.room.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        max_pk = Event.objects.latest('pk').pk
        response = self.client.post(url, data=data, follow=True)
        new_occurrences = []
        for occurrence in Event.objects.filter(pk__gt=max_pk).order_by('pk'):
            new_occurrences += [occurrence.pk]
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[another_day.conference.conference_slug]),
            another_day.conference.conference_slug,
            another_day.pk,
            str(new_occurrences).replace(" ", "%20"))
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
        self.assertTrue(new_vol_opp.approval_needed)

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
            'room': self.context.room.pk,
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
            'room': self.context.room.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response,
                            "bad is not one of the available choices.")

    def test_copy_class_not_supported(self):
        another_day = ConferenceDayFactory()
        target_context = ClassContext()
        url = reverse(self.view_name,
                      args=[target_context.sched_event.pk],
                      urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(403, response.status_code)
