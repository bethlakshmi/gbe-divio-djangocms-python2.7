from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    UserMessageFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    location,
    make_act_app_purchase,
    post_act_conflict,
)
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg,
    default_act_title_conflict,
)
from gbe.models import UserMessage


class TestEditAct(TestCase):
    '''Tests for edit_act view'''

    # this test case should be unnecessary, since edit_act should go away
    # for now, test it.
    view_name = 'act_edit'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()

    def get_act_form(self, act, submit=False, invalid=False):
        form_dict = {'theact-performer': act.performer.pk,
                     'theact-b_title': 'An act',
                     'theact-b_description': 'a description',
                     'theact-length_minutes': 60,
                     'theact-shows_preferences': [0],
                     'theact-act_duration': '1:00',
                     'theact-b_conference': act.b_conference.pk,
                     }
        if submit:
            form_dict['submit'] = 1
        if invalid:
            del(form_dict['theact-b_title'])
        return form_dict

    def post_edit_paid_act_submission(self, act_form=None):
        act = ActFactory()
        if not act_form:
            act_form = self.get_act_form(act, submit=True)

        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.performer_profile, self)
        make_act_app_purchase(
            act.b_conference,
            act.performer.performer_profile.user_object)
        response = self.client.post(
            url,
            data=act_form,
            follow=True)
        return response

    def post_title_collision(self):
        original = ActFactory()
        url = reverse(self.view_name,
                      args=[original.pk],
                      urlconf="gbe.urls")
        make_act_app_purchase(
            original.b_conference,
            original.performer.performer_profile.user_object)
        return post_act_conflict(
            original.b_conference,
            original.performer,
            self.get_act_form(original, submit=True),
            url,
            self)

    def post_edit_paid_act_draft(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.contact, self)
        response = self.client.post(url,
                                    self.get_act_form(act),
                                    follow=True)
        return response

    def test_edit_act_no_act(self):
        '''Should get 404 if no valid act ID'''
        profile = ProfileFactory()
        url = reverse(self.view_name,
                      args=[0],
                      urlconf="gbe.urls")
        login_as(profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_act_profile_is_not_contact(self):
        user = PersonaFactory().performer_profile.user_object
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_act_user_has_no_profile(self):
        user = UserFactory()
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(user, self)
        response = self.client.post(
            url,
            data=self.get_act_form(act, submit=True))
        self.assertEqual(response.status_code, 302)

    def test_act_edit_post_form_not_valid(self):
        '''act_edit, if form not valid, should return to ActEditForm'''
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.performer_profile, self)
        response = self.client.post(
            url,
            self.get_act_form(act, invalid=True))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Propose an Act' in response.content)

    def test_act_edit_post_form_submit_unpaid(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.performer_profile, self)
        response = self.client.post(
            url,
            data=self.get_act_form(act, submit=True))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Act Payment' in response.content)

    def test_act_edit_post_form_submit_paid_other_year(self):
        act = ActFactory()
        make_act_app_purchase(
            ConferenceFactory(
                status="completed"),
            act.performer.performer_profile.user_object)
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.performer_profile, self)
        response = self.client.post(
            url,
            data=self.get_act_form(act, submit=True))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Act Payment' in response.content)

    def test_edit_bid_post_no_submit(self):
        response = self.post_edit_paid_act_draft()
        redirect_tuple = ('http://testserver/gbe', 302)
        self.assertTrue(redirect_tuple in response.redirect_chain)
        self.assertTrue('Profile View' in response.content)

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(act.performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Propose an Act' in response.content)

    def test_edit_act_submit_make_message(self):
        response = self.post_edit_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_act_submit_msg)

    def test_edit_act_draft_make_message(self):
        response = self.post_edit_paid_act_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_act_draft_msg)

    def test_edit_act_submit_has_message(self):
        msg = UserMessageFactory(
            view='MakeActView',
            code='SUBMIT_SUCCESS')
        response = self.post_edit_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_edit_act_draft_has_message(self):
        msg = UserMessageFactory(
            view='MakeActView',
            code='DRAFT_SUCCESS')
        response = self.post_edit_paid_act_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_edit_act_title_collision(self):
        response, original = self.post_title_collision()
        self.assertEqual(response.status_code, 200)
        error_msg = default_act_title_conflict % (
            reverse(
                'act_edit',
                urlconf='gbe.urls',
                args=[original.pk]),
            original.b_title)
        assert_alert_exists(
            response, 'danger', 'Error', error_msg)

    def test_edit_act_title_collision_w_msg(self):
        message_string = "link: %s title: %s"
        msg = UserMessageFactory(
            view='MakeActView',
            code='ACT_TITLE_CONFLICT',
            description=message_string)
        response, original = self.post_title_collision()
        self.assertEqual(response.status_code, 200)
        error_msg = message_string % (
            reverse(
                'act_edit',
                urlconf='gbe.urls',
                args=[original.pk]),
            original.b_title)
        assert_alert_exists(
            response, 'danger', 'Error', error_msg)

    def test_edit_act_no_duration(self):
        act = ActFactory()
        act_form = self.get_act_form(act, submit=True)
        del act_form['theact-act_duration']
        response = self.post_edit_paid_act_submission(act_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
