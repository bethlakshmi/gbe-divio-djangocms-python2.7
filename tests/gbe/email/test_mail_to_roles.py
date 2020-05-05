from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    GenericEventFactory,
    ConferenceFactory,
    ProfileFactory,
    ProfilePreferencesFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_queued_email,
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.functions.gbe_email_functions import assert_checkbox
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
    VolunteerContext,
)
from gbetext import (
    group_filter_note,
    send_email_success_msg,
    to_list_empty_msg,
    unknown_request,
    unsubscribe_text,
)
from django.contrib.auth.models import User
from gbe.models import Conference
from gbetext import role_options
from gbe_forms_text import role_option_privs
from django.contrib.sites.models import Site


class TestMailToRoles(TestCase):
    view_name = 'mail_to_roles'
    role_list = ['Interested',
                 'Moderator',
                 "Panelist",
                 "Performer",
                 "Producer",
                 "Staff Lead",
                 "Teacher",
                 "Technical Director",
                 "Volunteer"]

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.privileged_user = User.objects.create_superuser(
            'myuser', 'myemail@test.com', "mypassword")
        self.privileged_profile = ProfileFactory(
            user_object=self.privileged_user)
        grant_privilege(self.privileged_profile.user_object,
                        "Schedule Mavens")
        self.context = ClassContext()
        self.url = reverse(self.view_name,
                           urlconf="gbe.email.urls")
        self.footer = unsubscribe_text % (
            Site.objects.get_current().domain,
            reverse(
                'email_update',
                urlconf='gbe.urls') + "?email_disable=send_role_notifications")

    def class_coord_login(self):
        limited_profile = ProfileFactory()
        grant_privilege(limited_profile.user_object, "Class Coordinator")
        login_as(limited_profile, self)

    def test_no_priv(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_full_login_first_get(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert_checkbox(
            response,
            "conference",
            0,
            self.context.conference.pk,
            self.context.conference.conference_slug,
            checked=False)
        n = 0
        for role in role_options:
            assert_checkbox(
                response,
                "roles",
                n,
                role[0],
                role[1],
                checked=False)
            n = n + 1
        self.assertContains(response, "Email Everyone")

    def test_reduced_login_first_get(self):
        for priv, roles in role_option_privs.items():
            limited_profile = ProfileFactory()
            grant_privilege(limited_profile.user_object,
                            priv)
            login_as(limited_profile, self)

            response = self.client.get(self.url, follow=True)
            assert_checkbox(
                response,
                "conference",
                0,
                self.context.conference.pk,
                self.context.conference.conference_slug,
                checked=False)
            n = 0
            for role in sorted(roles):
                assert_checkbox(
                    response,
                    "roles",
                    n,
                    role,
                    role,
                    checked=False)
                n = n + 1
        self.assertNotContains(response, "Email Everyone")

    def test_full_login_first_get_2_conf(self):
        extra_conf = ConferenceFactory()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert_checkbox(
            response,
            "conference",
            0,
            self.context.conference.pk,
            self.context.conference.conference_slug,
            checked=False)
        assert_checkbox(
            response,
            "conference",
            1,
            extra_conf.pk,
            extra_conf.conference_slug,
            checked=False)

    def test_pick_everyone(self):
        second_context = ClassContext()
        ProfilePreferencesFactory(
            profile=second_context.teacher.contact)

        login_as(self.privileged_profile, self)
        data = {
            'everyone': "Everyone",
        }
        response = self.client.post(self.url, data=data, follow=True)
        for user in User.objects.exclude(username="limbo"):
            self.assertContains(response, user.email)

    def test_pick_everyone_except_unsubscribed(self):
        ProfilePreferencesFactory(
            profile=self.context.teacher.contact,
            send_role_notifications=False)

        login_as(self.privileged_profile, self)
        data = {
            'everyone': "Everyone",
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(response, group_filter_note)

    def test_pick_conf_teacher(self):
        second_context = ClassContext()
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': self.role_list,
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            second_context.teacher.contact.user_object.email)

    def test_exclude_unsubscribed(self):
        ProfilePreferencesFactory(
            profile=self.context.teacher.contact,
            send_role_notifications=False)
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': self.role_list,
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)

    def test_pick_class_teacher(self):
        interested = self.context.set_interest()
        self.class_coord_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Teacher"],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            interested.user_object.email)
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Conference",
            "All Conference Classes",
            checked=False,
            prefix="event-select")

    def test_pick_all_conf_class(self):
        interested = self.context.set_interest()
        self.class_coord_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Teacher"],
            'event-select-event_collections': "Conference",
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            interested.user_object.email)
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Conference",
            "All Conference Classes",
            prefix="event-select")

    def test_pick_forbidden_role_reduced_priv(self):
        self.class_coord_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Teacher", "Performer"],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice. ' +
            'Performer is not one of the available choices.'
            )

    def test_pick_forbidden_collection_reduced_priv(self):
        self.class_coord_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Teacher", ],
            'event-select-event_collections': "Volunteer",
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice. ' +
            'Volunteer is not one of the available choices.'
            )

    def test_pick_performer_reduced_priv(self):
        showcontext = ShowContext()
        showcontext.show.e_title = "0 Pick Perf"
        showcontext.show.save()
        producer = showcontext.set_producer()
        anothershowcontext = ShowContext(
            conference=showcontext.conference,
        )
        anothershowcontext.show.e_title = "1 Pick Perf"
        anothershowcontext.show.save()
        login_as(producer, self)
        data = {
            'email-select-conference': [showcontext.conference.pk,
                                        self.context.conference.pk],
            'email-select-roles': ['Performer', ],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            showcontext.performer.contact.user_object.email)
        self.assertContains(
            response,
            anothershowcontext.performer.contact.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            showcontext.show.pk,
            showcontext.show.e_title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "events",
            1,
            anothershowcontext.show.pk,
            anothershowcontext.show.e_title,
            checked=False,
            prefix="event-select")

    def test_pick_performer_specific_show(self):
        showcontext = ShowContext()
        anothershowcontext = ShowContext(
            conference=showcontext.conference,
        )
        showcontext.show.e_title = "AAAAAAAA"
        showcontext.show.save()
        anothershowcontext.show.e_title = "ZZZZZZ"
        anothershowcontext.show.save()
        producer = showcontext.set_producer()
        login_as(producer, self)
        data = {
            'email-select-conference': [showcontext.conference.pk,
                                        self.context.conference.pk],
            'email-select-roles': ['Performer', ],
            'event-select-events': showcontext.show.pk,
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            anothershowcontext.performer.contact.user_object.email)
        self.assertContains(
            response,
            showcontext.performer.contact.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            showcontext.show.pk,
            showcontext.show.e_title,
            prefix="event-select")
        assert_checkbox(
            response,
            "events",
            1,
            anothershowcontext.show.pk,
            anothershowcontext.show.e_title,
            checked=False,
            prefix="event-select")

    def test_pick_performer_mismatch_show(self):
        showcontext = ShowContext()
        anothershowcontext = ShowContext()
        producer = showcontext.set_producer()
        login_as(producer, self)
        data = {
            'email-select-conference': [anothershowcontext.conference.pk],
            'email-select-roles': ['Performer', ],
            'event-select-events': showcontext.show.pk,
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            "%d is not one of the available choices." % showcontext.show.pk)

    def test_pick_staff_area_reduced_priv(self):
        staffcontext = StaffAreaContext()
        volunteer, booking = staffcontext.book_volunteer()
        special = GenericEventFactory(
            e_conference=staffcontext.conference)
        specialstaffcontext = VolunteerContext(
            event=special,
        )
        login_as(staffcontext.staff_lead, self)
        data = {
            'email-select-conference': [staffcontext.conference.pk, ],
            'email-select-roles': ['Volunteer', ],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            volunteer.user_object.email)
        self.assertContains(
            response,
            specialstaffcontext.profile.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            special.pk,
            special.e_title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "staff_areas",
            0,
            staffcontext.area.pk,
            staffcontext.area.title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Volunteer",
            "All Volunteer Events",
            checked=False,
            prefix="event-select")

    def test_pick_special_reduced_priv(self):
        staffcontext = StaffAreaContext()
        volunteer, booking = staffcontext.book_volunteer()
        special = GenericEventFactory(
            e_conference=staffcontext.conference)
        specialstaffcontext = VolunteerContext(
            event=special,
        )
        login_as(staffcontext.staff_lead, self)
        data = {
            'email-select-conference': [staffcontext.conference.pk, ],
            'email-select-roles': ['Volunteer', ],
            'event-select-events': special.pk,
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            volunteer.user_object.email)
        self.assertContains(
            response,
            specialstaffcontext.profile.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            special.pk,
            special.e_title,
            prefix="event-select")
        assert_checkbox(
            response,
            "staff_areas",
            0,
            staffcontext.area.pk,
            staffcontext.area.title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Volunteer",
            "All Volunteer Events",
            checked=False,
            prefix="event-select")

    def test_pick_drop_in(self):
        special = GenericEventFactory(
            e_conference=self.context.conference,
            type="Drop-In")
        specialstaffcontext = VolunteerContext(
            event=special,
            role="Teacher"
        )
        limited_profile = ProfileFactory()
        grant_privilege(limited_profile.user_object, "Registrar")
        login_as(limited_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk, ],
            'email-select-roles': ['Teacher', ],
            'event-select-event_collections': "Drop-In",
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            specialstaffcontext.profile.user_object.email)
        self.assertNotContains(
            response,
            special.e_title)
        assert_checkbox(
            response,
            "event_collections",
            1,
            "Drop-In",
            "All Drop-In Classes",
            prefix="event-select")

    def test_pick_area_reduced_priv(self):
        staffcontext = StaffAreaContext()
        volunteer, booking = staffcontext.book_volunteer()
        special = GenericEventFactory(
            e_conference=staffcontext.conference)
        specialstaffcontext = VolunteerContext(
            event=special,
        )
        login_as(staffcontext.staff_lead, self)
        data = {
            'email-select-conference': [staffcontext.conference.pk, ],
            'email-select-roles': ['Volunteer', ],
            'event-select-staff_areas': staffcontext.area.pk,
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            volunteer.user_object.email)
        self.assertNotContains(
            response,
            specialstaffcontext.profile.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            special.pk,
            special.e_title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "staff_areas",
            0,
            staffcontext.area.pk,
            staffcontext.area.title,
            prefix="event-select")
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Volunteer",
            "All Volunteer Events",
            checked=False,
            prefix="event-select")

    def test_pick_all_vol_reduced_priv(self):
        staffcontext = StaffAreaContext()
        volunteer, booking = staffcontext.book_volunteer()
        special = GenericEventFactory(
            e_conference=staffcontext.conference)
        specialstaffcontext = VolunteerContext(
            event=special,
        )
        login_as(staffcontext.staff_lead, self)
        data = {
            'email-select-conference': [staffcontext.conference.pk, ],
            'email-select-roles': ['Volunteer', ],
            'event-select-event_collections': "Volunteer",
            'refine': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            volunteer.user_object.email)
        self.assertContains(
            response,
            specialstaffcontext.profile.user_object.email)
        assert_checkbox(
            response,
            "events",
            0,
            special.pk,
            special.e_title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "staff_areas",
            0,
            staffcontext.area.pk,
            staffcontext.area.title,
            checked=False,
            prefix="event-select")
        assert_checkbox(
            response,
            "event_collections",
            0,
            "Volunteer",
            "All Volunteer Events",
            prefix="event-select")

    def test_pick_no_bidders(self):
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ['Interested', ],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', to_list_empty_msg)

    def test_send_email_success_status(self):
        staffcontext = StaffAreaContext(conference=self.context.conference)
        volunteer, booking = staffcontext.book_volunteer()
        login_as(self.privileged_profile, self)
        data = {
            'to': volunteer.user_object.email,
            'sender': self.privileged_profile.user_object.email,
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Performer", "Volunteer"],
            'event-select-staff_areas': staffcontext.area.pk,
            'event-select-event_collections': "Volunteer",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'success', 'Success', "%s%s" % (
                send_email_success_msg,
                volunteer.user_object.email))

    def test_send_email_success_email_sent(self):
        staffcontext = StaffAreaContext(conference=self.context.conference)
        volunteer, booking = staffcontext.book_volunteer()
        showcontext = ShowContext(conference=self.context.conference)
        showcontext.set_producer(producer=staffcontext.staff_lead)
        login_as(staffcontext.staff_lead, self)
        data = {
            'to': volunteer.user_object.email,
            'sender': staffcontext.staff_lead.user_object.email,
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Volunteer", ],
            'event-select-events': showcontext.show.pk,
            'event-select-staff_areas': staffcontext.area.pk,
            'event-select-event_collections': "Volunteer",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_queued_email(
            [volunteer.user_object.email, ],
            data['subject'],
            data['html_message'] + self.footer,
            data['sender'],
            )

    def test_send_email_failure_preserve_choices(self):
        staffcontext = StaffAreaContext(conference=self.context.conference)
        volunteer, booking = staffcontext.book_volunteer()
        showcontext = ShowContext(conference=self.context.conference)
        showcontext.set_producer(producer=staffcontext.staff_lead)
        login_as(self.privileged_profile, self)
        data = {
            'to': volunteer.user_object.email,
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-roles': ["Interested", ],
            'event-select-events': showcontext.show.pk,
            'event-select-staff_areas': staffcontext.area.pk,
            'event-select-event_collections': "Volunteer",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_checkbox(
            response,
            "conference",
            0,
            self.context.conference.pk,
            self.context.conference.conference_slug)
        assert_checkbox(
            response,
            "roles",
            0,
            "Interested",
            "Interested")
        assert_checkbox(
            response,
            "events",
            0,
            showcontext.show.pk,
            showcontext.show.e_title,
            prefix="event-select")
        assert_checkbox(
            response,
            "event_collections",
            2,
            "Volunteer",
            "All Volunteer Events",
            prefix="event-select")
