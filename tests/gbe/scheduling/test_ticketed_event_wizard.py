from django.test import TestCase
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ConferenceFactory,
    ConferenceDayFactory,
    ProfileFactory,
    RoomFactory,
)
from ticketing.models import (
    TicketingEvents,
    BrownPaperSettings,
)
from tests.factories.ticketing_factories import (
    TicketingEventsFactory,
    TicketTypeFactory,
    BrownPaperSettingsFactory,
)
from scheduler.models import Event
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    login_as,
)
from settings import GBE_DATE_FORMAT
from gbetext import link_event_to_ticket_success_msg
from tests.gbe.scheduling.test_scheduling import TestScheduling


class TestTicketedEventWizard(TestScheduling):
    '''This view makes Master and Drop In and associates them w. tickets'''
    view_name = 'create_ticketed_event_wizard'

    @classmethod
    def setUpTestData(cls):
        cls.room = RoomFactory()
        cls.teacher = BioFactory()
        cls.current_conference = ConferenceFactory()
        cls.room.conferences.add(cls.current_conference)
        cls.day = ConferenceDayFactory(conference=cls.current_conference)
        cls.url = reverse(
            cls.view_name,
            args=[cls.current_conference.conference_slug, "master"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=master"
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Scheduling Mavens')

    def edit_class(self):
        data = {
            'type': 'Master',
            'title': "Test Event Wizard",
            'description': 'Description',
            'slug': "MasterSlug",
            'conference': self.current_conference.pk,
            'max_volunteer': 1,
            'day': self.day.pk,
            'time': '11:00:00',
            'duration': 2.5,
            'location': self.room.pk,
            'set_event': 'Any value',
            'alloc_0-role': 'Teacher',
            'alloc_1-role': 'Volunteer',
        }
        return data

    def test_create_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access_master(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assert_event_was_picked_in_wizard(response, "master")
        self.assert_role_choice(response, "Teacher")
        self.assert_role_choice(response, "Volunteer")

    def test_authorized_user_can_access_dropin(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "drop-in"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=drop-in"
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assert_event_was_picked_in_wizard(response, "drop-in")
        self.assert_role_choice(response, "Teacher")
        self.assert_role_choice(response, "Volunteer")
        self.assert_role_choice(response, "Staff Lead")

    def test_authorized_user_can_access_special(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "special"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=special"
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assert_event_was_picked_in_wizard(response, "special")
        self.assert_role_choice(response, "Staff Lead")
        self.assertNotContains(response, "More...")

    def test_authorized_user_can_access_show(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "show"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=show"
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assert_event_was_picked_in_wizard(response, "show")
        self.assert_role_choice(response, "Producer")
        self.assert_role_choice(response, "Technical Director")
        self.assertNotContains(response, "More...")

    def test_authorized_user_can_also_get_volunteer_mgmt(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "show"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=show"
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, "More...")

    def test_authorized_user_can_access_master_no_tickets(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Set Tickets for Event")

    def test_authorized_user_can_access_master_and_tickets(self):
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set Tickets for Event")

    def test_auth_user_basic_scheduling(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            'Make New Class')
        self.assertContains(
            response,
            'name="duration" value="1"')
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (
                self.day.pk,
                self.day.day.strftime(GBE_DATE_FORMAT)
            ))

    def test_create_master(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.get(title=data['title'])
        self.assertEqual(occurrence.event_style, "Master")
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%d]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['title'],
                self.day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-success">\n       ' +
            '<td>%s</td>' % data['title'])
        self.assertEqual(occurrence.slug, "MasterSlug")

    def test_create_master_w_staffing(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['alloc_0-worker'] = self.teacher.pk
        data['alloc_1-worker'] = self.privileged_user.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.get(title=data['title'])
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%d]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['title'],
                self.day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-success">\n       ' +
            '<td>%s</td>' % data['title'])

    def test_create_dropin_w_staffing(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "drop-in"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=drop-in"
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['type'] = "Drop-In"
        data['alloc_0-role'] = "Staff Lead"
        data['alloc_1-role'] = "Teacher"
        data['alloc_2-role'] = "Volunteer"
        data['alloc_0-worker'] = self.privileged_user.pk
        data['alloc_1-worker'] = self.teacher.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.get(title=data['title'])
        self.assertEqual(occurrence.event_style, "Drop-In")
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%d]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['title'],
                self.day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-success">\n       ' +
            '<td>%s</td>' % data['title'])

    def test_create_show_w_staffing(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "show"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=show"
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['type'] = "Special"
        data['slug'] = "ShowSlug"
        data['alloc_0-role'] = "Producer"
        data['alloc_1-role'] = "Technical Director"
        data['alloc_0-worker'] = self.privileged_user.pk
        data['alloc_1-worker'] = self.teacher.contact.pk
        data['set_event'] = "More..."
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.get(title=data['title'])
        self.assertRedirects(
            response,
            "%s?volunteer_open=True&rehearsal_open=True" % reverse(
                'edit_show',
                urlconf='gbe.scheduling.urls',
                args=[self.current_conference.conference_slug,
                      occurrence.pk]))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['title'],
                self.day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertEqual(
            occurrence.slug, "ShowSlug"
        )

    def test_create_special_w_staffing(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "special"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=special"
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['type'] = "Special"
        data['alloc_0-role'] = "Staff Lead"
        data['alloc_0-worker'] = self.teacher.contact.pk
        data['set_event'] = "More..."
        data.pop('alloc_1-role', None)
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.get(title=data['title'])
        self.assertEqual(occurrence.event_style, "Special")
        self.assertRedirects(
            response,
            "%s?volunteer_open=True&rehearsal_open=True" % reverse(
                'edit_event',
                urlconf='gbe.scheduling.urls',
                args=[self.current_conference.conference_slug,
                      occurrence.pk]))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['title'],
                self.day.day.strftime(GBE_DATE_FORMAT))
            )

    def test_auth_user_bad_user_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['alloc_0-role'] = "bad role"
        data['alloc_1-role'] = "bad role"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "bad role is not one of the available choices.")

    def test_auth_user_bad_schedule_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['location'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(response, "This field is required.")

    def test_auth_user_bad_generic_booking_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['title'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "This field is required.")

    def test_get_tickets(self):
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        ticketing_event = TicketingEventsFactory(
            conference=self.current_conference)
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "%s - %s" % (ticketing_event.event_id,
                                                   ticketing_event.title))

    def test_set_ticketing_event(self):
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        ticketing_event = TicketingEventsFactory(
            conference=self.current_conference)
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['ticketing_events'] = ticketing_event.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.get(title=data['title'])
        self.assertEqual(occurrence.event_style, "Master")
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%d]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            link_event_to_ticket_success_msg + '%s - %s, ' % (
                ticketing_event.event_id,
                ticketing_event.title)
            )

    def test_set_ticket_type(self):
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        ticket = TicketTypeFactory(
            ticketing_event__conference=self.current_conference,
            ticketing_event__source=3)
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['ticket_types'] = ticket.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.get(title=data['title'])
        self.assertEqual(occurrence.event_style, "Master")
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%d]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            link_event_to_ticket_success_msg + '%s - %s, ' % (
                ticket.ticket_id,
                ticket.title)
            )
