from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    StaffAreaFactory,
    ProfileFactory,
    RoomFactory,
)
from gbe.models import StaffArea
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    grant_privilege,
    login_as,
)
from tests.functions.gbe_scheduling_functions import (
    assert_event_was_picked_in_wizard,
)


class TestStaffAreaWizard(TestCase):
    view_name = 'staff_area_wizard'

    def setUp(self):
        self.room = RoomFactory()
        self.current_conference = ConferenceFactory(accepting_bids=True)
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
        assert_event_was_picked_in_wizard(response, "staff")
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
            'Staff area has been created.<br>Title: %s' % data['title']
            )

    def test_auth_user_bad_user_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_area()
        data['staff_lead'] = "bad role"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "Something unusual has happened.")

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

    def test_create_area_w_all_vals_and_continue(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        data = self.edit_area()
        data['default_volunteers'] = 3
        data['staff_lead'] = self.privileged_user.profile.pk
        data['default_location'] = self.room.pk
        data['set_event'] = "More..."
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
            'Staff area has been created.<br>Title: %s' % (
                data['title'])
            )
        assert_option_state(response, self.room.pk, str(self.room), True)
        assert_option_state(response, self.privileged_user.profile.pk, 
                            str(self.privileged_user.profile), 
                            True)

        self.assertContains(
            response,
            'name="default_volunteers" value="3"')
