from django.urls import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    BioFactory,
    ConferenceFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
    assert_alert_exists,
)
from gbetext import (
    default_act_draft_msg,
    default_act_submit_msg,
    act_coord_instruct,
    missing_profile_info,
    no_comp_msg,
)
from gbe.models import (
    Conference,
    UserMessage,
)
from tests.functions.ticketing_functions import setup_fees
from ticketing.models import Transaction


class TestCoordinateAct(TestCase):
    '''Tests for create_act view'''
    view_name = 'act_coord_create'

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse(cls.view_name, urlconf='gbe.urls')
        Conference.objects.all().delete()
        cls.factory = RequestFactory()
        cls.performer = BioFactory(
            contact__phone="111-222-3333",
            contact__user_object__first_name="first",
            contact__user_object__last_name="last")
        cls.current_conference = ConferenceFactory(accepting_bids=True)
        UserMessage.objects.all().delete()
        cls.privileged_user = ProfileFactory.create().user_object
        grant_privilege(cls.privileged_user,
                        'Act Coordinator',
                        'assign_act')
        grant_privilege(cls.privileged_user,
                        'Act Reviewers')
        cls.url = reverse(cls.view_name, urlconf='gbe.urls')

    def get_act_form(self, persona=False, valid=True):
        if not persona:
            persona = self.performer
        form_dict = {'theact-b_title': 'An act',
                     'theact-track_title': 'a track',
                     'theact-track_artist': 'an artist',
                     'theact-b_description': 'a description',
                     'theact-bio': persona.pk,
                     'theact-act_duration': '1:00',
                     'theact-b_conference': self.current_conference.pk,
                     'submit': 1,
                     }
        if not valid:
            del(form_dict['theact-b_description'])
        return form_dict

    def post_act_submission(self, next_page=None, persona=False):
        act_form = self.get_act_form(persona)
        url = self.url
        if next_page is not None:
            url = "%s?next=%s" % (url, next_page)
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=act_form, follow=True)
        return response, act_form

    def test_bid_act_get_form(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, "Create Act for Coordinator")
        self.assertContains(response, act_coord_instruct)
        self.assertContains(response, "Submit &amp; Review")

    def test_act_bid_post_form_not_valid(self):
        login_as(self.privileged_user, self)
        data = self.get_act_form(valid=False)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Act for Coordinator")
        self.assertContains(response, "This field is required.")

    def test_act_submit_act_succeed(self):
        tickets = setup_fees(self.current_conference, is_act=True)
        response, data = self.post_act_submission()
        just_made = self.performer.acts.all().first()
        self.assertRedirects(response, reverse('act_review',
                                               urlconf="gbe.urls",
                                               args=[just_made.id]))
        self.assertContains(response, just_made.b_title)
        assert_alert_exists(
            response, 'success', 'Success', default_act_submit_msg)
        self.assertTrue(Transaction.objects.filter(
            purchaser__matched_to_user=just_made.performer.contact.user_object,
            ticket_item__ticketing_event__act_submission_event=True,
            ticket_item__ticketing_event__conference=self.current_conference
            ).exists())

    def test_act_submit_draft(self):
        tickets = setup_fees(self.current_conference, is_act=True)
        act_form = self.get_act_form()
        del(act_form['submit'])
        act_form['draft'] = 1
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=act_form, follow=True)
        just_made = self.performer.acts.all().first()
        self.assertRedirects(response, reverse('act_review_list',
                                               urlconf="gbe.urls"))
        assert_alert_exists(
            response, 'success', 'Success', default_act_draft_msg)
        self.assertTrue(Transaction.objects.filter(
            purchaser__matched_to_user=just_made.performer.contact.user_object,
            ticket_item__ticketing_event__act_submission_event=True,
            ticket_item__ticketing_event__conference=self.current_conference
            ).exists())

    def test_act_submit_act_incomplete_profile(self):
        incomplete = BioFactory()
        tickets = setup_fees(self.current_conference, is_act=True)
        response, data = self.post_act_submission(persona=incomplete)
        just_made = incomplete.acts.all().first()
        data['theact-bio'] = incomplete.pk
        self.assertRedirects(response, "%s?next=%s" % (
            reverse('admin_profile',
                    urlconf="gbe.urls",
                    args=[incomplete.contact.pk]),
            reverse('act_review', urlconf="gbe.urls", args=[just_made.id])))
        assert_alert_exists(
            response, 'warning', 'Warning', missing_profile_info)
        self.assertTrue(Transaction.objects.filter(
            purchaser__matched_to_user=incomplete.contact.user_object,
            ticket_item__ticketing_event__act_submission_event=True,
            ticket_item__ticketing_event__conference=self.current_conference
            ).exists())

    def test_act_submit_act_succeed_w_redirect(self):
        tickets = setup_fees(self.current_conference, is_act=True)
        response, data = self.post_act_submission(next_page="/theredirect")
        just_made = self.performer.acts.all().first()
        self.assertRedirects(response, "%s?next=/theredirect" % (
            reverse('act_review', urlconf="gbe.urls", args=[just_made.id])))
        self.assertContains(response, just_made.b_title)
        self.assertContains(response, "/theredirect")
        assert_alert_exists(
            response, 'success', 'Success', default_act_submit_msg)
        self.assertTrue(Transaction.objects.filter(
            purchaser__matched_to_user=just_made.performer.contact.user_object,
            ticket_item__ticketing_event__act_submission_event=True,
            ticket_item__ticketing_event__conference=self.current_conference
            ).exists())

    def test_act_submit_act_no_viable_ticket(self):
        response, data = self.post_act_submission()
        just_made = self.performer.acts.all().first()
        self.assertRedirects(response, reverse('act_review',
                                               urlconf="gbe.urls",
                                               args=[just_made.id]))
        assert_alert_exists(
            response, 'danger', 'Error', no_comp_msg)

    def test_bad_priv(self):
        login_as(self.performer.contact, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_act_title_collision(self):
        data = self.get_act_form()
        original = ActFactory(
            b_conference=self.current_conference,
            bio=self.performer)
        data['theact-b_title'] = original.b_title
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The act has the same title")
