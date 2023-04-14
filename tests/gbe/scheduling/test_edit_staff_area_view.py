from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.urls import reverse
from django.db.models import Max
from tests.factories.gbe_factories import (
    ConferenceDayFactory,
    ProfileFactory,
    RoomFactory,
)
from scheduler.models import Event
from gbe.models import Profile
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    grant_privilege,
    login_as,
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from datetime import timedelta


class TestEditStaffAreaView(TestCase):
    '''This view edits classes that were made through the wizard'''
    view_name = 'edit_staff'

    def setUp(self):
        self.room = RoomFactory()
        self.context = StaffAreaContext()
        self.context.area.default_volunteers = 7
        self.context.area.save()
        self.room.conferences.add(self.context.conference)
        self.url = reverse(
            self.view_name,
            args=[self.context.area.pk],
            urlconf='gbe.scheduling.urls')
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def edit_area(self):
        data = {
            'title': "Test Edit Staff",
            'slug': "New_slug",
            'conference': self.context.conference.pk,
            'description': 'Description',
            'default_volunteers': 3,
            'location': self.room.pk,
            'staff_lead': self.privileged_user.profile.pk,
            'edit_event': "Save and Return",
        }
        return data

    def test_edit_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Volunteer Management")
        self.assertContains(response, "Edit Staff Area Details")
        self.assertContains(response, self.context.area.title)
        self.assertContains(response, self.context.area.description)
        assert_option_state(
            response,
            self.context.staff_lead.profile.pk,
            str(self.context.staff_lead.profile),
            True)
        self.assertContains(
            response,
            'name="default_volunteers" value="7"')

    def test_authorized_user_can_get_volunteer_mgmt(self):
        self.context.area.default_location = self.room
        self.context.area.save()
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volunteer Management")
        self.assertContains(response, "Save and Continue")
        self.assertContains(
            response,
            'name="new_opp-max_volunteer" value="7"')
        self.assertContains(
            response,
            '<option value="%d" selected>%s</option>' % (
                self.room.pk,
                str(self.room)), 2)

    def test_vol_opp_present(self):
        self.context.area.default_room = self.room
        self.context.area.save()
        vol_opp = self.context.add_volunteer_opp()
        self.extra_day = ConferenceDayFactory(
            conference=self.context.conference,
            day=self.context.conf_day.day + timedelta(days=1))
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            'name="opp_sched_id" value="%d"' % (vol_opp.pk)
        )
        assert_option_state(
            response,
            self.context.conf_day.pk,
            self.context.conf_day.day.strftime("%b. %-d, %Y"),
            True)
        self.assertContains(
            response,
            'name="max_volunteer" value="7"')
        self.assertContains(response, "Display Staff", 2)

    def test_bad_staff_area(self):
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.area.pk+1000],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_edit_area(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data=self.edit_area(),
            follow=True)
        self.assertRedirects(
            response,
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Staff Area has been updated.<br>Title: Test Edit Staff')

    def test_edit_area_and_continue(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        data = self.edit_area()
        data['edit_event'] = "Save and Continue"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            "%s?volunteer_open=True" % self.url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Staff Area has been updated.<br>Title: %s' % (
                data['title']))
        self.assertContains(response, data['title'])
        self.assertContains(response, data['description'])
        assert_option_state(
            response,
            self.privileged_user.profile.pk,
            str(self.privileged_user.profile),
            True)
        self.assertContains(
            response,
            'name="default_volunteers" value="3"')

    def test_auth_user_bad_user_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_area()
        data['staff_lead'] = Profile.objects.aggregate(Max('pk'))['pk__max']+1
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "That choice is not one of the available choices.")

    def test_create_not_avail_room_fails(self):
        not_now_room = RoomFactory()
        login_as(self.privileged_user, self)
        data = self.edit_area()
        data['default_location'] = not_now_room.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "That choice is not one of the available choices.")

    def test_room_to_conf_mapping(self):
        not_now_room = RoomFactory()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room.name)
        self.assertNotContains(response, not_now_room.name)
