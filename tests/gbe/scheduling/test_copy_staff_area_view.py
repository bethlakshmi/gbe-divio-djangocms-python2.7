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
from gbe.models import StaffArea
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_hidden_value,
    assert_option_state,
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
    StaffAreaContext,
)
from gbe_forms_text import (
    copy_mode_labels,
    copy_mode_choices,
)
from gbetext import no_conf_day_msg


class TestCopyOccurrence(TestCase):
    view_name = 'copy_staff_schedule'
    copy_date_format = "%a, %b %-d, %Y %-I:%M %p"
    copy_children_only_checked = '<input type="radio" name="copy_mode" ' + \
        'value="copy_children_only" id="id_copy_mode_0" required checked />'

    def setUp(self):
        self.context = StaffAreaContext()
        self.vol_opp = self.context.add_volunteer_opp()
        self.url = reverse(
            self.view_name,
            args=[self.context.area.pk],
            urlconf='gbe.scheduling.urls')
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def assert_good_mode_form(self, response, title):
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.context.conf_day.day.strftime(GBE_DATE_FORMAT))
        self.assertContains(response, copy_mode_choices[0][1])
        self.assertContains(response, copy_mode_choices[1][1])

    def test_create_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Copying - %s" % self.context.area.title)

    def test_bad_area(self):
        url = reverse(
            self.view_name,
            args=[self.context.area.pk+100],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_authorized_user_get_no_conf_days(self):
        alt_context = StaffAreaContext()
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[alt_context.area.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse(
            'manage_event_list',
            urlconf='gbe.scheduling.urls',
            args=[alt_context.conference.conference_slug]))
        assert_alert_exists(
            response,
            'danger',
            'Error',
            no_conf_day_msg)

    def test_authorized_user_get_no_children(self):
        alt_context = StaffAreaContext()
        ConferenceDayFactory(conference=alt_context.conference)
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[alt_context.area.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.context.conf_day.day.strftime(GBE_DATE_FORMAT))
        self.assertNotContains(response, copy_mode_choices[0][1])

    def test_authorized_user_get_w_child_events(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_good_mode_form(
            response,
            self.context.area.title)

    def test_authorized_user_get_default_room(self):
        room = self.context.get_room()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_good_mode_form(
            response,
            self.context.area.title)
        assert_option_state(
            response,
            room.pk,
            room.name)

    def test_authorized_user_get_default_room_preset(self):
        room = self.context.get_room()
        self.context.area.default_location = room
        self.context.area.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_good_mode_form(
            response,
            self.context.area.title)
        assert_option_state(
            response,
            room.pk,
            room.name,
            True)

    def test_authorized_user_pick_mode_only_children(self):
        target_context = StaffAreaContext()
        delta = timedelta(days=340)
        target_day = ConferenceDayFactory(
            conference=target_context.conference,
            day=self.context.conf_day.day + delta)
        new_room = target_context.get_room()
        data = {
            'copy_mode': 'copy_children_only',
            'target_event': target_context.area.pk,
            'room': new_room.pk,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.copy_children_only_checked)
        self.assertContains(
            response,
            '<option value="%d" selected>' % (
                target_context.area.pk))
        self.assertContains(response, "Choose Sub-Events to be copied")
        self.assertContains(response, "%s - %s" % (
            self.vol_opp.eventitem.e_title,
            (self.vol_opp.start_time + delta).strftime(
                        self.copy_date_format)))
        assert_hidden_value(response, "id_room", "room", new_room.pk)

    def test_authorized_user_pick_mode_children_same_conf(self):
        target_context = StaffAreaContext(conference=self.context.conference)
        data = {
            'copy_mode': 'copy_children_only',
            'target_event': target_context.area.pk,
            'room': target_context.get_room().pk,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)
        print(response.content)
        self.assertContains(
            response,
            self.copy_children_only_checked)
        self.assertContains(
            response,
            '<option value="%d" selected>' % (
                target_context.area.pk))
        self.assertContains(response, "Choose Sub-Events to be copied")
        self.assertContains(response, "%s - %s" % (
            self.vol_opp.eventitem.e_title,
            self.vol_opp.start_time.strftime(self.copy_date_format)))

    def test_copy_child_event(self):
        target_context = StaffAreaContext()
        target_day = ConferenceDayFactory(
            conference=target_context.conference,
            day=self.context.conf_day.day + timedelta(days=340))
        new_room = target_context.get_room()
        data = {
            'copy_mode': 'copy_children_only',
            'target_event': target_context.area.pk,
            'copied_event': self.vol_opp.pk,
            'room': new_room.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)
        max_pk = Event.objects.latest('pk').pk
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[target_context.conference.conference_slug]),
            target_context.conference.conference_slug,
            target_day.pk,
            str([max_pk]),)
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, new_room)

    def test_copy_only_area(self):
        area_context = StaffAreaContext()
        conf_day = ConferenceDayFactory(
                conference=area_context.conference)
        another_day = ConferenceDayFactory()
        another_room = RoomFactory()
        another_room.conferences.add(another_day.conference)
        data = {
            'pick_mode': "Next",
            'copy_to_day': another_day.pk,
            'room': another_room.room.pk,
        }
        self.url = reverse(
            self.view_name,
            args=[area_context.area.pk],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[another_day.conference.conference_slug]),
            another_day.conference.conference_slug,
            another_day.pk,
            str([area_context.area.pk+1]))
        self.assertRedirects(response, redirect_url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'A new Staff Area was created.<br>Staff Area: %s' % (
                area_context.area.title))

    def test_copy_area_duplicate_name(self):
        dup_area_context = StaffAreaContext()
        dup_area_context.area.title = self.context.area.title
        dup_area_context.area.save()
        conf_day = ConferenceDayFactory(
                conference=dup_area_context.conference)
        self.url = reverse(
            self.view_name,
            args=[dup_area_context.area.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_to_day': self.context.conf_day.pk,
            'room': self.vol_opp.location.pk,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]),
            self.context.conference.conference_slug,
            self.context.conf_day.pk,
            str([dup_area_context.area.pk+1]))
        self.assertRedirects(response, redirect_url)
        max_area = StaffArea.objects.latest('pk')

        assert_alert_exists(
            response,
            'success',
            'Success',
            'A new Staff Area was created.<br>Staff Area: %s' % (
                max_area.title))

    def test_copy_child_parent_events(self):
        another_day = ConferenceDayFactory()
        another_room = RoomFactory()
        another_room.conferences.add(another_day.conference)
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk,
            'copied_event': self.vol_opp.pk,
            'room': another_room.room.pk,
            'pick_event': "Finish",
        }
        self.vol_opp.approval_needed = True
        self.vol_opp.save()
        login_as(self.privileged_user, self)
        max_pk = Event.objects.latest('pk').pk
        response = self.client.post(self.url, data=data, follow=True)
        new_occurrences = []
        for occurrence in Event.objects.filter(pk__gt=max_pk):
            new_occurrences += [occurrence.pk]
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s&alt_id=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[another_day.conference.conference_slug]),
            another_day.conference.conference_slug,
            another_day.pk,
            str(new_occurrences).replace(" ", "%20"),
            self.context.area.pk+1)
        self.assertRedirects(response, redirect_url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'A new Staff Area was created.<br>Staff Area: %s' % (
                self.context.area.title))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s' % (
                self.vol_opp.eventitem.e_title,
                datetime.combine(
                    another_day.day,
                    self.vol_opp.starttime.time()).strftime(
                    GBE_DATETIME_FORMAT)))
        self.assertContains(response, "bid-table approval_needed", 2)

    def test_copy_child_parent_events_same_conf(self):
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': self.context.conf_day.pk,
            'copied_event': self.vol_opp.pk,
            'room': self.vol_opp.location.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        max_pk = Event.objects.latest('pk').pk
        response = self.client.post(self.url, data=data, follow=True)
        new_occurrences = []
        max_area = StaffArea.objects.latest('pk')
        for occurrence in Event.objects.filter(pk__gt=max_pk):
            new_occurrences += [occurrence.pk]
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s&alt_id=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]),
            self.context.conference.conference_slug,
            self.context.conf_day.pk,
            str(new_occurrences).replace(" ", "%20"),
            max_area.pk)
        self.assertRedirects(response, redirect_url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'A new Staff Area was created.<br>Staff Area: %s' % (
                max_area.title))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s' % (
                self.vol_opp.eventitem.e_title,
                datetime.combine(
                    self.context.conf_day.day,
                    self.vol_opp.starttime.time()).strftime(
                    GBE_DATETIME_FORMAT)))
        self.assertNotContains(response, "bid-table approval_needed")

    def test_copy_child_parent_events_keep_room(self):
        new_room = self.context.get_room()
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': self.context.conf_day.pk,
            'copied_event': self.vol_opp.pk,
            'room': new_room.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(response, new_room.name)

    def test_copy_only_parent_event(self):
        another_day = ConferenceDayFactory()
        another_room = RoomFactory()
        another_room.conferences.add(another_day.conference)
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk,
            'room': another_room.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)
        max_area = StaffArea.objects.latest('pk')
        redirect_url = "%s?%s-day=%d&filter=Filter&alt_id=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[another_day.conference.conference_slug]),
            another_day.conference.conference_slug,
            another_day.pk,
            max_area.pk,)
        self.assertRedirects(response, redirect_url)
        self.assertRedirects(response, redirect_url)
        self.assertFalse(max_area.default_location)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'A new Staff Area was created.<br>Staff Area: %s' % (
                max_area.title))

    def test_copy_parent_event_change_room(self):
        another_day = ConferenceDayFactory()
        another_room = RoomFactory()
        another_room.conferences.add(another_day.conference)
        orig_room = self.context.get_room()
        self.context.area.default_location = orig_room
        self.context.area.save()
        data = {
            'copy_mode': 'include_parent',
            'copy_to_day': another_day.pk,
            'room': another_room.pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)
        max_area = StaffArea.objects.latest('pk')
        self.assertEqual(another_room, max_area.default_location)

    def test_copy_child_event_fail_no_conf(self):
        target_context = StaffAreaContext()
        self.url = reverse(
            self.view_name,
            args=[target_context.area.pk],
            urlconf='gbe.scheduling.urls')
        data = {
            'copy_mode': 'copy_children_only',
            'target_event': target_context.area.pk,
            'copied_event': self.vol_opp.pk,
            'room': target_context.get_room().pk,
            'pick_event': "Finish",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(response, reverse(
            'manage_event_list',
            urlconf='gbe.scheduling.urls',
            args=[target_context.conference.conference_slug]))
        assert_alert_exists(
            response,
            'danger',
            'Error',
            no_conf_day_msg)
