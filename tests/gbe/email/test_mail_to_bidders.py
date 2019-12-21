from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ClassFactory,
    ConferenceFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_queued_email,
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts.class_context import (
    ClassContext,
)
from gbetext import (
    acceptance_states,
    send_email_success_msg,
    to_list_empty_msg,
    unknown_request,
)
from django.contrib.auth.models import User
from gbe.models import Conference
from post_office.models import Email
from tests.functions.gbe_email_functions import assert_checkbox


class TestMailToBidder(TestCase):
    view_name = 'mail_to_bidders'
    priv_list = ['Act', 'Class', 'Costume', 'Vendor', 'Volunteer']

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.privileged_user = User.objects.create_superuser(
            'myuser', 'myemail@test.com', "mypassword")
        self.privileged_profile = ProfileFactory(
            user_object=self.privileged_user)
        for priv in self.priv_list:
            grant_privilege(
                self.privileged_profile.user_object,
                '%s Coordinator' % priv)
        self.context = ClassContext()
        self.url = reverse(self.view_name,
                           urlconf="gbe.email.urls")

    def reduced_login(self):
        reduced_profile = ProfileFactory()
        grant_privilege(
            reduced_profile.user_object,
            '%s Coordinator' % "Act")
        login_as(reduced_profile, self)
        return reduced_profile

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = "%s/?next=/email/mail_to_bidders" % (
            reverse('login', urlconf='gbe.urls'))
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_no_priv(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_full_login_first_get(self):
        n = 0
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert_checkbox(
            response,
            "conference",
            0,
            self.context.conference.pk,
            self.context.conference.conference_slug)
        for priv in self.priv_list:
            assert_checkbox(
                response,
                "bid_type",
                n,
                priv,
                priv)
            n = n + 1
        for state in acceptance_states:
            self.assertContains(
                response,
                'value="%s"' % state[0])
            self.assertContains(
                response,
                state[1])
        self.assertContains(response, "Email Everyone")

    def test_reduced_login_first_get(self):
        self.reduced_login()
        response = self.client.get(self.url, follow=True)
        assert_checkbox(
            response,
            "conference",
            0,
            self.context.conference.pk,
            self.context.conference.conference_slug)
        assert_checkbox(
            response,
            "bid_type",
            0,
            "Act",
            "Act")
        self.assertNotContains(
            response,
            '"Class"')
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
            self.context.conference.conference_slug)
        assert_checkbox(
            response,
            "conference",
            1,
            extra_conf.pk,
            extra_conf.conference_slug)

    def test_pick_everyone(self):
        login_as(self.privileged_profile, self)
        data = {
            'everyone': "Everyone",
        }
        response = self.client.post(self.url, data=data, follow=True)
        for user in User.objects.exclude(username="limbo"):
            self.assertContains(response, user.email)

    def test_pick_everyone_no_priv(self):
        self.reduced_login()
        data = {
            'everyone': "Everyone",
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', unknown_request)

    def test_pick_conf_bidder(self):
        second_context = ClassContext()
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            second_context.teacher.contact.user_object.email)

    def test_pick_class_bidder(self):
        second_bid = ActFactory()
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk,
                                        second_bid.b_conference.pk],
            'email-select-bid_type': ["Class"],
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            second_bid.performer.contact.user_object.email)

    def test_pick_status_bidder(self):
        second_class = ClassFactory(accepted=2)
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk,
                                        second_class.b_conference.pk],
            'email-select-bid_type': ["Class"],
            'email-select-state': [3],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            second_class.teacher.contact.user_object.email)

    def test_pick_class_draft(self):
        second_bid = ClassFactory()
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk,
                                        second_bid.b_conference.pk],
            'email-select-bid_type': ["Class"],
            'email-select-state': ["Draft"],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            second_bid.teacher.contact.user_object.email)

    def test_pick_class_draft_and_accept(self):
        second_bid = ClassFactory()
        third_bid = ClassFactory(submitted=True)
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk,
                                        second_bid.b_conference.pk,
                                        third_bid.b_conference.pk],
            'email-select-bid_type': ["Class"],
            'email-select-state': ["Draft", 3],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            second_bid.teacher.contact.user_object.email)
        self.assertNotContains(
            response,
            third_bid.teacher.contact.user_object.email)

    def test_pick_forbidden_bid_type_reduced_priv(self):
        second_bid = ActFactory()
        self.reduced_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': "Class",
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice. Class is not one of the available choices.'
            )

    def test_pick_reduced_priv(self):
        second_bid = ActFactory(submitted=True)
        self.reduced_login()
        data = {
            'email-select-conference': [self.context.conference.pk,
                                        second_bid.b_conference.pk],
            'email-select-bid_type': ['Act'],
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertNotContains(
            response,
            self.context.teacher.contact.user_object.email)
        self.assertContains(
            response,
            second_bid.performer.contact.user_object.email)

    def test_pick_no_bidders(self):
        reduced_profile = self.reduced_login()
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': ['Act'],
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'filter': True,
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', to_list_empty_msg)

    def test_pick_admin_has_sender(self):
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'filter': "Filter",
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            '<input type="email" name="sender" ' +
            'value="%s" required id="id_sender" />' % (
                self.privileged_profile.user_object.email))

    def test_pick_no_admin_fixed_email(self):
        act_bid = ActFactory(submitted=True)
        reduced_profile = self.reduced_login()
        data = {
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'email-select-bid_type': ['Act'],
            'email-select-conference': [act_bid.b_conference.pk],
            'filter': "Filter",
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            '<input type="hidden" name="sender" ' +
            'value="%s" id="id_sender" />' % (
                reduced_profile.user_object.email))

    def test_send_email_success_status(self):
        login_as(self.privileged_profile, self)
        data = {
            'to': self.context.teacher.contact.user_object.email,
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'success', 'Success', "%s%s" % (
                send_email_success_msg,
                self.context.teacher.contact.user_object.email))

    def test_send_email_success_email_sent(self):
        login_as(self.privileged_profile, self)
        data = {
            'to': self.context.teacher.contact.user_object.email,
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_queued_email(
            [self.context.teacher.contact.user_object.email, ],
            data['subject'],
            data['html_message'],
            data['sender'],
            )

    def test_send_email_reduced_w_fixed_from(self):
        reduced_profile = self.reduced_login()
        second_bid = ActFactory(submitted=True)
        data = {
            'to': second_bid.performer.contact.user_object.email,
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk,
                                        second_bid.b_conference.pk],
            'email-select-bid_type': ['Act'],
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_queued_email(
            [second_bid.performer.contact.user_object.email, ],
            data['subject'],
            data['html_message'],
            reduced_profile.user_object.email,
            )

    def test_send_email_reduced_no_hack(self):
        reduced_profile = self.reduced_login()
        second_bid = ActFactory()
        data = {
            'to': second_bid.performer.contact.user_object.email,
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk,
                                        second_bid.b_conference.pk],
            'email-select-bid_type': "Class",
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice. Class is not one of the available choices.'
            )

    def test_send_email_reduced_to_list_no_hack(self):
        reduced_profile = self.reduced_login()
        second_bid = ActFactory(submitted=True)
        random = ProfileFactory()
        data = {
            'to': [second_bid.performer.contact.user_object.email,
                   random.user_object.email],
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk,
                                        second_bid.b_conference.pk],
            'email-select-bid_type': ['Act'],
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            'Select a valid choice. %s is %s' % (
                random.user_object.email,
                'not one of the available choices.'))

    def test_send_email_failure(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(response, "This field is required.", 2)

    def test_send_email_failure_preserve_to_list(self):
        login_as(self.privileged_profile, self)
        data = {
            'to': self.context.teacher.contact.user_object.email,
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        to_string = '<input type="checkbox" name="to" value="%s" checked ' + \
            'class="form-check-input" id="id_to_0" />%s'
        self.assertContains(
            response,
            to_string % (self.context.teacher.contact.user_object.email,
                         self.context.teacher.contact.display_name))

    def test_send_email_failure_preserve_conference_choice(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_checkbox(
            response,
            "conference",
            0,
            self.context.conference.pk,
            self.context.conference.conference_slug)

    def test_send_email_failure_preserve_bid_type_choice(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': "Class",
            'email-select-state': [0, 1, 2, 3, 4, 5],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_checkbox(
            response,
            "bid_type",
            1,
            "Class",
            "Class")

    def test_send_email_failure_preserve_state_choice(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [3, ],
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(
            response,
            '<input type="checkbox" name="email-select-state" value="3" ' +
            'checked class="form-check-input" id="id_email-select-state_4" ' +
            '/>')

    def test_pick_no_post_action(self):
        second_class = ClassFactory(accepted=2)
        login_as(self.privileged_profile, self)
        data = {
            'email-select-conference': [self.context.conference.pk],
            'email-select-bid_type': self.priv_list,
            'email-select-state': [0, 1, 2, 3, 4, 5],
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', unknown_request)

    def test_send_everyone_success_email_sent(self):
        login_as(self.privileged_profile, self)
        data = {
            'to': User.objects.exclude(
                username="limbo").values_list('email', flat=True),
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'everyone': "Everyone",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        for user in User.objects.exclude(username="limbo"):
            assert_queued_email(
                [user.email, ],
                data['subject'],
                data['html_message'],
                data['sender'],
                )

    def test_send_everyone_reduced(self):
        reduced_profile = self.reduced_login()
        data = {
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'everyone': "Everyone",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', unknown_request)

    def test_send_everyone_success_alert_displayed(self):
        User.objects.exclude(
            username=self.privileged_profile.user_object.username).delete()
        second_super = User.objects.create_superuser(
            'secondsuper', 'secondsuper@test.com', "mypassword")
        login_as(self.privileged_profile, self)
        data = {
            'to': [self.privileged_profile.user_object.email,
                   second_super.email],
            'sender': "sender@admintest.com",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'everyone': "Everyone",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'success', 'Success', "%s%s, %s" % (
                send_email_success_msg,
                self.privileged_profile.user_object.email,
                second_super.email))
