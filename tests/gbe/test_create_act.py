from django.urls import reverse
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
    login_as,
    assert_alert_exists,
    make_act_app_purchase,
    make_act_app_ticket,
    post_act_conflict,
)
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg,
    default_act_title_conflict,
    fee_instructions,
)
from gbe.models import (
    Conference,
    UserMessage,
)
from tests.functions.ticketing_functions import setup_fees
from datetime import (
    datetime,
    timedelta,
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

    def post_unpaid_act_draft(self):
        login_as(self.performer.performer_profile, self)
        POST = self.get_act_form()
        POST['draft'] = True
        response = self.client.post(self.url, data=POST, follow=True)
        return response, POST

    def test_bid_act_no_personae(self):
        '''act_bid, when profile has no personae,
        should redirect to persona-add'''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, "%s?next=%s" % (
            reverse('persona-add', urlconf="gbe.urls", args=[1]),
            self.url))

    def test_bid_act_get_with_persona(self):
        '''act_bid, when profile has a personae'''
        profile = PersonaFactory().performer_profile
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(url)
        expected_string = "Propose an Act"
        self.assertContains(response, expected_string)

    def test_act_bid_post_no_performer(self):
        '''act_bid, user has no performer, should redirect to persona-add'''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.post(self.url, data=self.get_act_form())
        expected_loc = '%s?next=%s' % (
            reverse('persona-add', urlconf="gbe.urls", args=[1]),
            self.url)
        self.assertRedirects(response, expected_loc)

    def test_act_bid_post_form_not_valid(self):
        login_as(self.performer.performer_profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        data = self.get_act_form(submit=True, valid=False)
        response = self.client.post(url,
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')

    def test_act_bid_post_submit_no_payment(self):
        '''act_bid, if user has not paid, should take us to please_pay'''
        login_as(self.performer.performer_profile, self)
        tickets = setup_fees(self.current_conference, is_act=True)
        POST = self.get_act_form()
        POST.update({'submit': '',
                     'donation': 10})
        response = self.client.post(self.url, data=POST)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Act Submission Fee")

    def test_act_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems,
        should redirect to home'''
        make_act_app_purchase(self.current_conference,
                              self.performer.performer_profile.user_object)
        response, data = self.post_unpaid_act_draft()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ' - Fee has been paid, submit NOW!')
        assert_alert_exists(
            response, 'success', 'Success', default_act_draft_msg)

    def test_act_bid_not_paid(self):
        '''act_bid, not post, not paid should take us to bid process'''
        tickets = setup_fees(self.current_conference, is_act=True)
        login_as(self.performer.performer_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        self.assertContains(response, "Fee (pay what you will)")

    def test_act_bid_not_paid_w_fee_within_date_limit(self):
        '''act_bid, not post, show the ticket price in active range'''
        tickets = setup_fees(self.current_conference,
                             is_act=True)
        tickets[0].start_time = datetime.now() - timedelta(days=5)
        tickets[0].end_time = datetime.now() + timedelta(days=5)
        tickets[0].save()
        login_as(self.performer.performer_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        self.assertContains(response, "Fee (pay what you will)")
        self.assertContains(response, 'value="%5.2f"' % tickets[0].cost)

    def test_act_bid_not_paid_w_fee_outside_date_limit(self):
        '''act_bid, several viable tickets are before and after current day'''
        tickets_shown = setup_fees(self.current_conference, is_act=True)
        ticket_later = setup_fees(self.current_conference, is_act=True)
        ticket_sooner = setup_fees(self.current_conference, is_act=True)
        ticket_later[0].start_time = datetime.now() + timedelta(days=3)
        ticket_later[0].cost = tickets_shown[0].cost - 1
        ticket_sooner[0].end_time = datetime.now() - timedelta(days=3)
        ticket_later[0].cost = tickets_shown[0].cost - 2
        ticket_later[0].save()
        ticket_sooner[0].save()
        login_as(self.performer.performer_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        self.assertContains(response, "Fee (pay what you will)")
        self.assertContains(response, 'value="%5.2f"' % tickets_shown[0].cost)

    def test_act_bid_not_post(self):
        '''act_bid, not post, not paid should take us to bid process'''
        make_act_app_purchase(self.current_conference,
                              self.performer.performer_profile.user_object)
        msg = UserMessageFactory(
            view='MakeActView',
            code='BID_INSTRUCTIONS',
            summary="Act Bid Instructions",
            description="Test Bid Instructions Message")
        login_as(self.performer.performer_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        self.assertNotContains(response, fee_instructions)
        self.assertContains(response, "Test Bid Instructions Message")
        self.assertContains(response, 'value="Submit For Approval"')

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
        response, data = self.post_unpaid_act_draft()
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

    def test_act_draft_hacked_performer(self):
        make_act_app_purchase(self.current_conference,
                              self.performer.performer_profile.user_object)
        response, data = self.post_unpaid_act_draft()
        other_performer = PersonaFactory()
        other_profile = other_performer.performer_profile
        data['theact-performer'] = other_performer.pk
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ' - Fee has been paid, submit NOW!')
        assert_alert_exists(
            response, 'success', 'Success', default_act_draft_msg)
