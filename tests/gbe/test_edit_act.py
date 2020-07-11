from django.urls import reverse
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
    payment_needed_msg,
    payment_details_error,
)
from gbe.models import UserMessage
from tests.functions.ticketing_functions import setup_fees


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
        act_form = self.get_act_form(act)
        act_form['draft'] = True
        response = self.client.post(url,
                                    act_form,
                                    follow=True)
        return response

    def test_edit_act_no_act(self):
        '''Should get 404 if no valid act ID'''
        profile = ProfileFactory()
        url = reverse(self.view_name,
                      args=[0],
                      urlconf="gbe.urls")
        login_as(profile, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_edit_act_profile_is_not_contact(self):
        user = PersonaFactory().performer_profile.user_object
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(user, self)
        response = self.client.get(url, follow=True)
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
        self.assertContains(response, 'Propose an Act')

    def test_act_edit_post_form_submit_unpaid(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        tickets = setup_fees(act.b_conference, is_act=True)
        login_as(act.performer.performer_profile, self)
        act_form = self.get_act_form(act, submit=True)
        act_form['donation'] = 10
        response = self.client.post(url, data=act_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Act Submission Fee")
        self.assertContains(response, payment_needed_msg)

    def test_act_edit_post_form_submit_bad_pay_choice(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        tickets = setup_fees(act.b_conference, is_act=True)
        login_as(act.performer.performer_profile, self)
        act_form = self.get_act_form(act, submit=True)
        act_form['donation'] = 5
        response = self.client.post(url, data=act_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, payment_details_error)
        self.assertContains(
            response,
            "Ensure this value is greater than or equal to 10.00")

    def test_act_edit_post_form_submit_paid_other_year(self):
        act = ActFactory()
        make_act_app_purchase(
            ConferenceFactory(
                status="completed"),
            act.performer.performer_profile.user_object)
        tickets = setup_fees(act.b_conference, is_act=True)

        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.performer_profile, self)
        act_form = self.get_act_form(act, submit=True)
        act_form['donation'] = 10
        response = self.client.post(url, data=act_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Act Payment')

    def test_edit_bid_post_no_submit(self):
        response = self.post_edit_paid_act_draft()
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        self.assertContains(response, 'Profile View')

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory(shows_preferences="[u'0']",
                         other_performance="[u'1', u'3']")
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(act.performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        constraint_selected = '<input type="checkbox" name="theact-%s" ' + \
            'value="%d" id="id_theact-%s_%d" checked />'
        self.assertContains(response, constraint_selected % (
            "shows_preferences",
            0,
            "shows_preferences",
            0))
        self.assertContains(response, constraint_selected % (
            "other_performance",
            1,
            "other_performance",
            1))
        self.assertContains(response, constraint_selected % (
            "other_performance",
            3,
            "other_performance",
            3))

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
