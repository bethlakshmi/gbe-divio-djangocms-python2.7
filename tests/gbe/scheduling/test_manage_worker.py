from django.test import (
    TestCase,
    Client
)
from django.urls import reverse
from tests.factories.gbe_factories import (
    EmailTemplateSenderFactory,
    ProfileFactory,
    ProfilePreferencesFactory,
)
from tests.contexts import StaffAreaContext
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_email_template_used,
    assert_option_state,
    grant_privilege,
    is_login_page,
    login_as,
)
from django.shortcuts import get_object_or_404
from gbe.models import Volunteer
from django.contrib.sites.models import Site
from gbetext import (
    role_commit_map,
    volunteer_allocate_email_fail_msg,
)
from django.core import mail


class TestManageWorker(TestCase):
    view_name = "manage_workers"
    get_param = "?email_disable=send_schedule_change_notifications"

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.user = ProfileFactory.create().user_object
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Volunteer Coordinator')
        grant_privilege(cls.privileged_user, 'Scheduling Mavens')
        cls.context = StaffAreaContext()
        cls.conference = cls.context.conference
        cls.volunteer_opp = cls.context.add_volunteer_opp()
        cls.volunteer, cls.alloc = cls.context.book_volunteer(
            cls.volunteer_opp)
        cls.url = reverse(
            cls.view_name,
            args=[cls.context.conference.conference_slug,
                  cls.volunteer_opp.pk],
            urlconf="gbe.scheduling.urls")
        cls.unsub_link = Site.objects.get_current().domain + reverse(
            'email_update',
            urlconf='gbe.urls',
            args=[cls.volunteer.user_object.email])

    def get_edit_data(self):
        data = self.get_either_data()
        data['alloc_id'] = self.alloc.pk
        return data

    def get_create_data(self):
        data = self.get_either_data()
        data['alloc_id'] = -1
        return data

    def get_either_data(self):
        data = {'worker': self.volunteer.pk,
                'role': 'Volunteer',
                'label': 'Do these notes work?'}
        return data

    def assert_post_contents(self,
                             response,
                             conference,
                             volunteer_opp,
                             volunteer,
                             alloc,
                             notes,
                             role="Volunteer",
                             allocations=2):
        assert_option_state(response,
                            str(volunteer.pk),
                            str(volunteer),
                            True)
        assert_option_state(response,
                            role,
                            role,
                            True)

        self.assertContains(
            response,
            '<input type="hidden" name="alloc_id" value="' +
            str(alloc.pk) + '" id="id_alloc_id" />',
            html=True)
        self.assertContains(
            response,
            '<input type="text" name="label" value="' + notes +
            '" maxlength="100" id="id_label" />',
            html=True)
        self.assertContains(
            response,
            '<form method="POST" action="%s' % (reverse(
                'manage_workers',
                urlconf='gbe.scheduling.urls',
                args=[conference.conference_slug,
                      volunteer_opp.pk])))

    def assert_good_post(self,
                         response,
                         conference,
                         volunteer_opp,
                         volunteer,
                         alloc,
                         notes,
                         role="Volunteer",
                         allocations=2):
        self.assertRedirects(
            response,
            "%s?worker_open=True&changed_id=%d" % (
                reverse(
                    'edit_volunteer',
                    urlconf='gbe.scheduling.urls',
                    args=[conference.conference_slug,
                          volunteer_opp.pk]),
                alloc.pk))
        self.assert_post_contents(response,
                                  conference,
                                  volunteer_opp,
                                  volunteer,
                                  alloc,
                                  notes,
                                  role,
                                  allocations,)
        self.assertNotContains(response, '<ul class="errorlist">')
        self.assertContains(response, role_commit_map[role][1])

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('login') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.post(self.url, data=self.get_create_data())
        self.assertEqual(response.status_code, 403)

    def test_post_form_valid_make_new_allocation(self):
        context = StaffAreaContext()
        volunteer_opp = context.add_volunteer_opp()
        allocations = volunteer_opp.resources_allocated.all()
        volunteer = ProfileFactory()
        url = reverse(self.view_name,
                      args=[context.conference.conference_slug,
                            volunteer_opp.pk],
                      urlconf="gbe.scheduling.urls")
        data = self.get_create_data()
        data['worker'] = volunteer.pk,

        login_as(self.privileged_profile, self)
        response = self.client.post(url, data=data, follow=True)
        alloc = volunteer_opp.peopleallocation_set.all().order_by(
            'pk').reverse().first()

        self.assertIsNotNone(alloc)
        self.assert_good_post(
            response,
            context.conference,
            volunteer_opp,
            volunteer,
            alloc,
            'Do these notes work?',
            allocations=3)

    def test_post_form_edit_exiting_allocation(self):
        new_volunteer = ProfileFactory()
        data = self.get_edit_data()
        data['worker'] = new_volunteer.pk,
        data['role'] = 'Producer',

        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assert_good_post(
            response,
            self.conference,
            self.volunteer_opp,
            new_volunteer,
            self.alloc,
            'Do these notes work?',
            "Producer")

    def test_post_form_edit_to_waitlisted(self):
        new_volunteer = ProfileFactory()
        data = self.get_edit_data()
        data['worker'] = new_volunteer.pk,
        data['role'] = 'Waitlisted',

        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assert_good_post(
            response,
            self.conference,
            self.volunteer_opp,
            new_volunteer,
            self.alloc,
            'Do these notes work?',
            "Waitlisted")
        assert_email_template_used(
            "Your volunteer proposal has changed status to Wait List")

    def test_post_form_edit_to_rejected(self):
        new_volunteer = ProfileFactory()
        data = self.get_edit_data()
        data['worker'] = new_volunteer.pk,
        data['role'] = 'Rejected',

        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assert_good_post(
            response,
            self.conference,
            self.volunteer_opp,
            new_volunteer,
            self.alloc,
            'Do these notes work?',
            "Rejected")
        assert_email_template_used(
            "Your volunteer proposal has changed status to Reject")

    def test_post_form_edit_bad_label(self):
        big_label = 'Do these notes work?Do these notes work?' + \
                    'Do these notes work?Do these notes work?' + \
                    'Do these notes work?Do these notes work?' + \
                    'Do these notes work?Do these notes work?'
        data = self.get_edit_data()
        data['label'] = big_label

        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assert_post_contents(
            response,
            self.conference,
            self.volunteer_opp,
            self.volunteer,
            self.alloc,
            big_label)
        self.assertContains(
            response,
            '<li>Ensure this value has at most 100 characters ' +
            '(it has ' + str(len(big_label)) + ').</li>')
        self.assertContains(response, role_commit_map['Error'][1])

    def test_post_form_edit_bad_role(self):
        data = self.get_edit_data()
        data['role'] = ''

        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assert_post_contents(
            response,
            self.conference,
            self.volunteer_opp,
            self.volunteer,
            self.alloc,
            'Do these notes work?')
        self.assertContains(
            response,
            '<li>This field is required.</li>')
        self.assertContains(response, role_commit_map['Error'][1])

    def test_post_form_edit_bad_role_and_booking(self):
        data = self.get_edit_data()
        data['role'] = ''
        data['alloc_id'] = self.alloc.pk + 100
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            'BOOKING_NOT_FOUND  Booking id %s for occurrence %d not found' % (
                self.alloc.pk + 100,
                self.volunteer_opp.pk))

    def test_post_form_create_bad_role(self):
        data = self.get_create_data()
        data['role'] = '',

        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assert_post_contents(
            response,
            self.conference,
            self.volunteer_opp,
            self.volunteer,
            self.alloc,
            'Do these notes work?')
        self.assertContains(
            response,
            '<li>This field is required.</li>')
        self.assertContains(
            response,
            'title="Delete" type="submit" name="delete" value="Delete">',
            count=1)
        self.assertContains(
            response,
            'title="Edit" type="submit" name="edit" value="Edit">',
            count=1)
        self.assertContains(
            response,
            'title="Create New" type="submit" name="create" value="Create">',
            count=1)
        self.assertContains(response, role_commit_map['Error'][1])

    def test_post_form_valid_delete_allocation(self):
        data = self.get_edit_data()
        data['delete'] = 1
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(
            response,
            "%s?worker_open=True&changed_id=%d" % (
                reverse('edit_volunteer',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug,
                              self.volunteer_opp.pk]),
                self.alloc.pk))
        self.assertNotContains(
            response,
            '<option value="%d" selected>%s</option>' % (
                self.volunteer.pk,
                str(self.volunteer)))
        self.assertNotContains(
            response,
            '<input type="hidden" name="alloc_id" value="' +
            str(self.alloc.pk) + '" id="id_alloc_id" />')
        self.assertContains(
            response,
            '<form method="POST" action="%s' % (reverse(
                self.view_name,
                urlconf='gbe.scheduling.urls',
                args=[self.context.conference.conference_slug,
                      self.volunteer_opp.pk])))
        self.assertContains(response, role_commit_map['New'][1])

    def test_post_form_valid_delete_allocation_sends_notification(self):
        data = self.get_edit_data()
        data['delete'] = 1
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(
            response,
            "%s?worker_open=True&changed_id=%d" % (
                reverse('edit_volunteer',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug,
                              self.volunteer_opp.pk]),
                self.alloc.pk))
        msg = assert_email_template_used(
            "A change has been made to your Volunteer Schedule!")
        assert("http://%s%s" % (
            Site.objects.get_current().domain,
            reverse('home', urlconf='gbe.urls')) in msg.body)
        assert(self.unsub_link in msg.body)
        assert(self.get_param in msg.body)

    def test_post_form_valid_notification_template_fail(self):
        EmailTemplateSenderFactory(
            from_email="scheduleemail@notify.com",
            template__name='volunteer schedule update',
            template__subject="test template",
            template__content="stuff {% url 'gbehome' %}  more stuff"
        )
        data = self.get_edit_data()
        data['delete'] = 1
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(
            response,
            "%s?worker_open=True&changed_id=%d" % (
                reverse('edit_volunteer',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug,
                              self.volunteer_opp.pk]),
                self.alloc.pk))
        self.assertContains(response,
                            volunteer_allocate_email_fail_msg)

    def test_post_form_valid_delete_allocation_w_bad_data(self):
        data = self.get_edit_data()
        data['role'] = ''
        data['delete'] = 1
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'This field is required.')

    def test_post_form_valid_delete_allocation_w_no_alloc(self):
        data = self.get_edit_data()
        data['alloc_id'] = ''
        data['delete'] = 1
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            'NO_BOOKING  No booking id for occurrence id %d.' % (
                self.volunteer_opp.pk))

    def test_post_form_valid_delete_allocation_w_bad_alloc(self):
        data = self.get_edit_data()
        data['alloc_id'] = self.alloc.pk + 100
        data['delete'] = 1
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            'BOOKING_NOT_FOUND  Could not find booking id ' +
            '%d for occurrence id %d.' % (self.alloc.pk + 100,
                                          self.volunteer_opp.pk))

    def test_post_form_edit_exiting_alloc_used_email_tmpl(self):
        new_volunteer = ProfileFactory()
        data = self.get_edit_data()
        data['worker'] = new_volunteer.pk,
        data['role'] = 'Producer',
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        msg = assert_email_template_used(
            "A change has been made to your Volunteer Schedule!")
        self.unsub_link = Site.objects.get_current().domain + reverse(
            'email_update',
            urlconf='gbe.urls',
            args=[new_volunteer.user_object.email])
        assert(self.unsub_link in msg.body)
        assert(self.get_param in msg.body)

    def test_post_form_edit_exclude_unsubscribed(self):
        new_volunteer = ProfileFactory()
        data = self.get_edit_data()
        data['worker'] = new_volunteer.pk,
        data['role'] = 'Producer',
        ProfilePreferencesFactory(
            profile=new_volunteer,
            send_schedule_change_notifications=False)
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertEqual(0, len(mail.outbox))

    def test_post_form_edit_notification_template_fail(self):
        EmailTemplateSenderFactory(
            from_email="scheduleemail@notify.com",
            template__name='volunteer schedule update',
            template__subject="test template",
            template__content="stuff {% url 'gbehome' %}  more stuff"
        )
        new_volunteer = ProfileFactory()
        data = self.get_edit_data()
        data['worker'] = new_volunteer.pk,
        data['role'] = 'Producer',
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(response,
                            volunteer_allocate_email_fail_msg)

    def test_post_form_valid_make_new_allocation_w_confict(self):
        data = self.get_create_data()
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            'SCHEDULE_CONFLICT  <br>- Affected user: %s<br>- ' % (
                self.volunteer.display_name) +
            'Conflicting booking: %s, Start Time: %s' % (
                self.volunteer_opp.title,
                'Fri, Feb 5 12:00 PM')
            )

    def test_post_form_valid_make_new_allocation_w_overfull(self):
        data = self.get_create_data()
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(response, "Over booked by 1 volunteers")

    def test_post_form_edit_w_conflict(self):
        overbook_opp = self.context.add_volunteer_opp()
        self.context.book_volunteer(
            volunteer_sched_event=overbook_opp,
            volunteer=self.volunteer)
        data = self.get_edit_data()
        login_as(self.privileged_profile, self)
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            'SCHEDULE_CONFLICT  <br>- Affected user: %s<br>- ' % (
                self.volunteer.display_name) +
            'Conflicting booking: %s, Start Time: %s' % (
                overbook_opp.title,
                'Fri, Feb 5 12:00 PM')
            )
