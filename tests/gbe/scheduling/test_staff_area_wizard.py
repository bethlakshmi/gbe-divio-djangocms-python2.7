from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.urls import reverse
from django.db.models import Max
from tests.factories.gbe_factories import (
    ConferenceFactory,
    StaffAreaFactory,
    ProfileFactory,
    RoomFactory,
)
from gbe.models import (
    Profile,
    StaffArea,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    grant_privilege,
    login_as,
)
from tests.gbe.scheduling.test_scheduling import TestScheduling
from gbetext import slug_safety_msgs


class TestStaffAreaWizard(TestScheduling):
    view_name = 'staff_area_wizard'

    def setUp(self):
        self.room = RoomFactory()
        self.current_conference = ConferenceFactory()
        self.room.conferences.add(self.current_conference)
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=staff"
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def edit_area(self):
        data = {
            'title': "Test Staff Wizard",
            'slug': "new_staff_area",
            'description': 'Description',
            'conference': self.current_conference.pk,
            'set_event': 'Save and Return to List',
            'staff_lead': '',
        }
        return data

    def test_create_staff_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assert_event_was_picked_in_wizard(response, "staff")
        self.assertContains(response, "Select Event Type: Staff Area")
        self.assertContains(response, "Create Staff Area")

    def test_authorized_user_can_also_get_volunteer_mgmt(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=show"
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, "More..")

    def test_create_area(self):
        login_as(self.privileged_user, self)
        data = self.edit_area()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        new_area = StaffArea.objects.get(slug=data['slug'],
                                         conference=self.current_conference)
        self.assertEqual(new_area.conference, self.current_conference)
        self.assertRedirects(
            response,
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.current_conference.conference_slug]))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Staff Area has been updated.<br>Title: %s' % data['title']
            )

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

    def test_auth_user_dup_slug(self):
        login_as(self.privileged_user, self)
        StaffAreaFactory(conference=self.current_conference,
                         slug="new_staff_area")
        data = self.edit_area()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "Staff area with this Slug and Conference already exists.")

    def test_auth_user_dup_title(self):
        login_as(self.privileged_user, self)
        StaffAreaFactory(conference=self.current_conference,
                         title="Test Staff Wizard")
        data = self.edit_area()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "Staff area with this Title and Conference already exists.")

    def test_create_area_w_all_vals_and_continue_w_warning(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        data = self.edit_area()
        data['default_volunteers'] = 3
        data['staff_lead'] = self.privileged_user.profile.pk
        data['default_location'] = self.room.pk
        data['set_event'] = "More..."
        data['slug'] = "Conference"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        new_area = StaffArea.objects.get(slug=data['slug'],
                                         conference=self.current_conference)
        self.assertRedirects(
            response,
            "%s?start_open=False" % reverse(
                'edit_staff',
                urlconf='gbe.scheduling.urls',
                args=[new_area.id]))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Staff Area has been updated.<br>Title: %s' % (
                data['title'])
            )
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            '%s<br>Slug: Conference' % slug_safety_msgs['cal_type']
            )
        assert_option_state(response, self.room.pk, str(self.room), True)
        assert_option_state(response, self.privileged_user.profile.pk,
                            str(self.privileged_user.profile),
                            True)

        self.assertContains(
            response,
            'name="default_volunteers" value="3"')

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
