import nose.tools as nt
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    UserMessageFactory,
)
from tests.functions.gbe_functions import (
    location,
    login_as,
    current_conference,
    assert_alert_exists,
    make_act_app_purchase,
    post_act_conflict,
)
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg,
    default_act_title_conflict,
)
from gbe.models import (
    Conference,
    UserMessage,
)


class TestCreateAct(TestCase):
    '''Tests for create_act view'''
    view_name = 'act_create'

    def setUp(self):
        self.url = reverse(self.view_name, urlconf='gbe.urls')
        Conference.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.current_conference = ConferenceFactory(accepting_bids=True)
        UserMessage.objects.all().delete()

    def get_act_form(self, submit=False, valid=True):

        form_dict = {'theact-shows_preferences': [1],
                     'theact-b_title': 'An act',
                     'theact-track_title': 'a track',
                     'theact-track_artist': 'an artist',
                     'theact-b_description': 'a description',
                     'theact-performer': self.performer.resourceitem_id,
                     'theact-act_duration': '1:00',
                     'theact-b_conference': self.current_conference.pk
                     }
        if submit:
            form_dict['submit'] = 1
        if not valid:
            del(form_dict['theact-b_description'])
        return form_dict

    def post_paid_act_submission(self, act_form=None):
        if not act_form:
            act_form = self.get_act_form()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        act_form.update({'submit': ''})
        make_act_app_purchase(self.current_conference,
                              self.performer.performer_profile.user_object)
        response = self.client.post(url, data=act_form, follow=True)
        return response, act_form

    def post_paid_act_draft(self):
        current_conference()
        login_as(self.performer.performer_profile, self)
        POST = self.get_act_form()
        response = self.client.post(self.url, data=POST, follow=True)
        return response, POST

    def test_bid_act_no_personae(self):
        '''act_bid, when profile has no personae,
        should redirect to persona_create'''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_bid_act_get_with_persona(self):
        '''act_bid, when profile has no personae,
        should redirect to persona_create'''
        profile = PersonaFactory().performer_profile
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(url)
        expected_string = "Propose an Act"
        nt.assert_true(expected_string in response.content)
        nt.assert_equal(response.status_code, 200)

    def test_act_bid_post_no_performer(self):
        '''act_bid, user has no performer, should redirect to persona_create'''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.post(self.url, data=self.get_act_form())
        self.assertEqual(response.status_code, 302)

    def test_act_bid_post_form_not_valid(self):
        login_as(self.performer.performer_profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        data = self.get_act_form(submit=True, valid=False)
        response = self.client.post(url,
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Propose an Act' in response.content)

    def test_act_bid_post_submit_no_payment(self):
        '''act_bid, if user has not paid, should take us to please_pay'''
        current_conference()
        login_as(self.performer.performer_profile, self)
        POST = self.get_act_form()
        POST.update({'submit': ''})
        response = self.client.post(self.url, data=POST)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Fee has not been Paid' in response.content)

    def fake_verify_performer_app_paid(user_name):
        return True

    def test_act_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems,
        should redirect to home'''
        current_conference()
        response, data = self.post_paid_act_draft()
        self.assertEqual(response.status_code, 200)
        act_name = data['theact-b_title']
        expected_string = "%s - Not submitted" % act_name
        assert expected_string in response.content
        self.assertContains(response, data['theact-b_title'])

    def test_act_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        login_as(self.performer.performer_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Propose an Act' in response.content)

    def test_act_submit_paid_act(self):
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View</a> act")
        self.assertContains(response, data['theact-b_title'])

    def test_act_submit_paid_act_w_other_acts_paid(self):
        ActFactory(b_conference=self.current_conference,
                   submitted=True)
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View</a> act")
        self.assertContains(response, data['theact-b_title'])

    def test_act_submit_paid_act_w_old_comp_act(self):
        prev_act = ActFactory(
            submitted=True,
            performer=self.performer,
            b_conference=ConferenceFactory(status='completed'))
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View</a> act")
        self.assertContains(response, data['theact-b_title'])

    def test_act_submit_paid_act_w_old_comp_act(self):
        prev_act = ActFactory(
            submitted=True,
            performer=self.performer,
            b_conference=ConferenceFactory(status='completed'))
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View</a> act")
        self.assertContains(response, data['theact-b_title'])

    def test_act_submit_second_paid_act(self):
        prev_act = ActFactory(
            submitted=True,
            performer=self.performer,
            b_conference=self.current_conference)
        make_act_app_purchase(self.current_conference,
                              self.performer.performer_profile.user_object)
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View</a> act")
        self.assertContains(response, data['theact-b_title'])

    def test_act_submit_make_message(self):
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_act_submit_msg)

    def test_act_draft_make_message(self):
        response, data = self.post_paid_act_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_act_draft_msg)

    def test_act_submit_has_message(self):
        msg = UserMessageFactory(
            view='MakeActView',
            code='SUBMIT_SUCCESS')
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_act_draft_has_message(self):
        msg = UserMessageFactory(
            view='MakeActView',
            code='DRAFT_SUCCESS')
        response, data = self.post_paid_act_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_act_title_collision(self):
        response, original = post_act_conflict(
            self.current_conference,
            self.performer,
            self.get_act_form(),
            self.url,
            self)
        self.assertEqual(response.status_code, 200)
        error_msg = default_act_title_conflict % (
            reverse(
                'act_edit',
                urlconf='gbe.urls',
                args=[original.pk]),
            original.b_title)
        assert_alert_exists(
            response, 'danger', 'Error', error_msg)

    def test_act_title_collision_w_msg(self):
        message_string = "link: %s title: %s"
        msg = UserMessageFactory(
            view='MakeActView',
            code='ACT_TITLE_CONFLICT',
            description=message_string)
        response, original = post_act_conflict(
            self.current_conference,
            self.performer,
            self.get_act_form(),
            self.url,
            self)
        self.assertEqual(response.status_code, 200)
        error_msg = message_string % (
            reverse(
                'act_edit',
                urlconf='gbe.urls',
                args=[original.pk]),
            original.b_title)
        assert_alert_exists(
            response, 'danger', 'Error', error_msg)

    def test_act_submit_paid_act_no_duration(self):
        form = self.get_act_form()
        del form['theact-act_duration']
        response, data = self.post_paid_act_submission(form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
