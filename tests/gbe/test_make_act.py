from django.urls import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    BioFactory,
    ConferenceFactory,
    ProfileFactory,
    UserMessageFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    assert_alert_exists,
    make_act_app_purchase,
    make_act_app_ticket,
)
from gbetext import (
    act_group_needs_names,
    default_act_submit_msg,
    default_act_draft_msg,
    default_act_title_conflict,
    fee_instructions,
    payment_details_error,
    payment_needed_msg,
)
from gbe.models import (
    Conference,
    Profile,
    UserMessage,
)
from tests.functions.ticketing_functions import setup_fees
from datetime import (
    datetime,
    timedelta,
)


class TestMakeAct(TestCase):

    @classmethod
    def setUpTestData(cls):
        Conference.objects.all().delete()
        cls.current_conference = ConferenceFactory()

    def setUp(self):
        self.client = Client()

    def get_act_form(self, performer, submit=False):

        form_dict = {'theact-shows_preferences': [8],
                     'theact-phone': '111-222-3333',
                     'theact-first_name': 'Jane',
                     'theact-last_name': 'Smith',
                     'theact-b_title': 'An act',
                     'theact-track_title': 'a track',
                     'theact-track_artist': 'an artist',
                     'theact-b_description': 'a description',
                     'theact-num_performers': 1,
                     'theact-bio': performer.pk,
                     'theact-act_duration': '1:00',
                     'theact-b_conference': self.current_conference.pk
                     }
        if submit:
            form_dict['submit'] = 1
        return form_dict

    def check_subway_state(self, response, active_state="Apply"):
        self.assertContains(
            response,
            '<li class="progressbar_active">%s</li>' % active_state,
            html=True)
        if active_state != "Payment":
            self.assertContains(
                response,
                '<li class="progressbar_upcoming">Payment</li>',
                html=True)


class TestCreateAct(TestMakeAct):
    '''Tests for create_act view'''
    view_name = 'act_create'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse(cls.view_name, urlconf='gbe.urls')
        cls.performer = BioFactory()

    def post_paid_act_submission(self, act_form=None):
        if not act_form:
            act_form = self.get_act_form(self.performer)
        login_as(self.performer.contact, self)
        act_form.update({'submit': ''})
        make_act_app_purchase(self.current_conference,
                              self.performer.contact.user_object)
        response = self.client.post(self.url, data=act_form, follow=True)
        return response, act_form

    def post_unpaid_act_draft(self):
        login_as(self.performer.contact, self)
        POST = self.get_act_form(self.performer)
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
            reverse('persona-add', urlconf="gbe.urls"),
            self.url))
        self.check_subway_state(response, active_state="Create Bio")

    def test_bid_act_get_with_persona(self):
        '''act_bid, when profile has a personae'''
        profile = BioFactory().contact
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(url)
        expected_string = "Propose an Act"
        self.assertContains(response, expected_string)
        self.check_subway_state(response)

    def test_act_bid_post_form_not_valid(self):
        login_as(self.performer.contact, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        data = {'submit': 1}
        response = self.client.post(url,
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        self.assertContains(response, "Performer is not valid")
        self.check_subway_state(response)

    def test_act_bid_post_submit_no_payment(self):
        '''act_bid, if user has not paid, should take us to please_pay'''
        login_as(self.performer.contact, self)
        tickets = setup_fees(self.current_conference, is_act=True)
        POST = self.get_act_form(self.performer)
        POST.update({'submit': '',
                     'donation': 10})
        response = self.client.post(self.url, data=POST)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Act Submission Fee")
        self.check_subway_state(response, active_state="Payment")

    def test_act_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems,
        should redirect to home'''
        make_act_app_purchase(self.current_conference,
                              self.performer.contact.user_object)
        response, data = self.post_unpaid_act_draft()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ' - Fee has been paid, submit NOW!')
        assert_alert_exists(
            response, 'success', 'Success', default_act_draft_msg)

    def test_act_bid_not_paid_w_fee_within_date_limit(self):
        '''act_bid, not post, show the ticket price in active range'''
        tickets = setup_fees(self.current_conference,
                             is_act=True)
        tickets[0].start_time = datetime.now() - timedelta(days=5)
        tickets[0].end_time = datetime.now() + timedelta(days=5)
        tickets[0].save()
        login_as(self.performer.contact, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        self.assertContains(response, "Fee (pay what you will)")
        self.assertContains(response, 'value="%5.2f"' % tickets[0].cost)
        self.check_subway_state(response)

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
        login_as(self.performer.contact, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        self.assertContains(response, "Fee (pay what you will)")
        self.assertContains(response, 'value="%5.2f"' % tickets_shown[0].cost)

    def test_act_bid_not_post(self):
        '''act_bid, not post, but paid should take us to bid process'''
        UserMessage.objects.all().delete()
        make_act_app_purchase(self.current_conference,
                              self.performer.contact.user_object)
        msg = UserMessageFactory(
            view='MakeActView',
            code='BID_INSTRUCTIONS',
            summary="Act Bid Instructions",
            description="Test Bid Instructions Message")
        login_as(self.performer.contact, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        self.assertNotContains(response, fee_instructions)
        self.assertContains(response, "Test Bid Instructions Message")
        self.assertContains(response, 'value="Submit For Approval"')
        self.check_subway_state(response)

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
            bio=self.performer,
            b_conference=ConferenceFactory(status='completed'))
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View</a> act")
        self.assertContains(response, data['theact-b_title'])

    def test_act_submit_second_paid_act(self):
        prev_act = ActFactory(
            submitted=True,
            bio=self.performer,
            b_conference=self.current_conference)
        make_act_app_purchase(self.current_conference,
                              self.performer.contact.user_object)
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View</a> act")
        self.assertContains(response, data['theact-b_title'])

    def test_act_draft_hacked_performer(self):
        make_act_app_purchase(self.current_conference,
                              self.performer.contact.user_object)
        response, data = self.post_unpaid_act_draft()
        other_performer = BioFactory()
        other_profile = other_performer.contact
        data['theact-performer'] = other_performer.pk
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ' - Fee has been paid, submit NOW!')
        assert_alert_exists(
            response, 'success', 'Success', default_act_draft_msg)


class TestEditAct(TestMakeAct):
    '''Tests for edit_act view'''

    # this test case should be unnecessary, since edit_act should go away
    # for now, test it.
    view_name = 'act_edit'

    def post_edit_paid_act_submission(self, act_form=None):
        act = ActFactory()
        if not act_form:
            act_form = self.get_act_form(act.performer, submit=True)

        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.contact, self)
        make_act_app_purchase(
            act.b_conference,
            act.performer.contact.user_object)
        response = self.client.post(
            url,
            data=act_form,
            follow=True)
        return response

    def post_title_collision(self, submit_state=False):
        original = ActFactory(submitted=submit_state)
        duplicate_edit = ActFactory(b_conference=original.b_conference,
                                    bio=original.bio)
        make_act_app_purchase(
            duplicate_edit.b_conference,
            duplicate_edit.performer.contact.user_object)
        login_as(duplicate_edit.performer.contact, self)
        data = self.get_act_form(original.performer, submit=True)
        data['theact-b_title'] = original.b_title
        data['theact-b_conference'] = original.b_conference.pk

        url = reverse(self.view_name,
                      args=[duplicate_edit.pk],
                      urlconf="gbe.urls")
        response = self.client.post(url, data=data, follow=True)
        return response, original

    def post_edit_paid_act_draft(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.contact, self)
        act_form = self.get_act_form(act.performer)
        act_form['draft'] = True
        act_form['theact-b_title'] = '"extra quotes"'
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
        user = BioFactory().contact.user_object
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(user, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_act_edit_post_form_trigger_group_name_check(self):
        '''act_edit, if form not valid, should return to ActEditForm'''
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        tickets = setup_fees(act.b_conference, is_act=True)
        login_as(act.performer.contact, self)
        data = self.get_act_form(act.performer, submit=True)
        data['donation'] = 10
        data['theact-num_performers'] = 3
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        self.check_subway_state(response)
        self.assertContains(response, act_group_needs_names)

    def test_act_edit_post_form_submit_unpaid(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        tickets = setup_fees(act.b_conference, is_act=True)
        login_as(act.performer.contact, self)
        act_form = self.get_act_form(act.performer, submit=True)
        act_form['donation'] = 10
        response = self.client.post(url, data=act_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Act Submission Fee")
        self.assertContains(response, payment_needed_msg)
        profile = Profile.objects.get(pk=act.performer.contact.pk)
        self.assertEqual(profile.phone, '111-222-3333')
        self.assertEqual(profile.user_object.first_name, 'Jane')
        self.assertEqual(profile.user_object.last_name, 'Smith')
        self.check_subway_state(response, active_state="Payment")

    def test_act_edit_post_form_submit_bad_pay_choice(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        tickets = setup_fees(act.b_conference, is_act=True)
        login_as(act.performer.contact, self)
        act_form = self.get_act_form(act.performer, submit=True)
        act_form['donation'] = 5
        response = self.client.post(url, data=act_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, payment_details_error)
        self.assertContains(
            response,
            "Ensure this value is greater than or equal to 10.00")
        self.check_subway_state(response)

    def test_act_edit_post_form_submit_paid_other_year(self):
        act = ActFactory()
        make_act_app_purchase(
            ConferenceFactory(
                status="completed"),
            act.performer.contact.user_object)
        tickets = setup_fees(act.b_conference, is_act=True)

        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.contact, self)
        act_form = self.get_act_form(act.performer, submit=True)
        act_form['donation'] = 10
        response = self.client.post(url, data=act_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Act Payment')
        self.check_subway_state(response, active_state="Payment")

    def test_edit_bid_post_no_submit(self):
        response = self.post_edit_paid_act_draft()
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        self.assertContains(response, 'Welcome to GBE')
        self.assertContains(response, 'extra quotes')
        self.assertNotContains(response, '"extra quotes"')

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory(shows_preferences="[u'9']")
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        act.performer.contact.phone = "555-666-7777"
        act.performer.contact.user_object.first_name = "Bee"
        act.performer.contact.user_object.last_name = "Bumble"
        act.performer.contact.save()
        login_as(act.performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Propose an Act')
        constraint_selected = '<input type="checkbox" name="theact-%s" ' + \
            'value="%d" id="id_theact-%s_%d" checked />'
        self.assertContains(
            response,
            constraint_selected % (
                "shows_preferences",
                9,
                "shows_preferences",
                1),
            html=True)
        self.assertContains(response, act.performer.contact.phone)
        self.assertContains(
            response,
            act.performer.contact.user_object.first_name)
        self.assertContains(
            response,
            act.performer.contact.user_object.last_name)
        self.check_subway_state(response)

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
        self.check_subway_state(response)

    def test_edit_act_title_collision_w_msg(self):
        message_string = "link: %s title: %s"
        msg = UserMessageFactory(
            view='MakeActView',
            code='ACT_TITLE_CONFLICT',
            description=message_string)
        response, original = self.post_title_collision(submit_state=True)
        self.assertEqual(response.status_code, 200)
        error_msg = message_string % (
            reverse(
                'act_view',
                urlconf='gbe.urls',
                args=[original.pk]),
            original.b_title)
        assert_alert_exists(
            response, 'danger', 'Error', error_msg)
        self.check_subway_state(response)

    def test_edit_act_no_duration(self):
        act = ActFactory()
        act_form = self.get_act_form(act.performer, submit=True)
        del act_form['theact-act_duration']
        response = self.post_edit_paid_act_submission(act_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.check_subway_state(response)
