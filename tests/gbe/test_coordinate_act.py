from django.urls import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
    assert_alert_exists,
)
from gbetext import (
    default_act_submit_msg,
    act_coord_instruct,
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
        cls.performer = PersonaFactory()
        cls.current_conference = ConferenceFactory(accepting_bids=True)
        UserMessage.objects.all().delete()
        cls.privileged_user = ProfileFactory.create().user_object
        grant_privilege(cls.privileged_user,
                        'Act Coordinator',
                        'assign_act')
        grant_privilege(cls.privileged_user,
                        'Act Reviewers')

    def get_act_form(self, valid=True):
        form_dict = {'theact-b_title': 'An act',
                     'theact-track_title': 'a track',
                     'theact-track_artist': 'an artist',
                     'theact-b_description': 'a description',
                     'theact-performer': self.performer.resourceitem_id,
                     'theact-act_duration': '1:00',
                     'theact-b_conference': self.current_conference.pk,
                     'theact-accepted': 3,
                     'submit': 1,
                     }
        if not valid:
            del(form_dict['theact-b_description'])
        return form_dict

    def post_act_submission(self, next_page=None):
        act_form = self.get_act_form()
        url = reverse(self.view_name, urlconf='gbe.urls')
        if next_page is not None:
            url = "%s?next=%s" % (url, next_page)
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=act_form, follow=True)
        return response, act_form

    def test_bid_act_get_form(self):
        '''act_bid, when profile has a personae'''
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertContains(response, "Create Act for Coordinator")
        self.assertContains(response, act_coord_instruct)

    def test_act_bid_post_form_not_valid(self):
        login_as(self.privileged_user, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        data = self.get_act_form(valid=False)
        response = self.client.post(url, data=data)
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
        login_as(self.performer.performer_profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_act_title_collision(self):
        url = reverse(self.view_name, urlconf='gbe.urls')
        data = self.get_act_form()
        original = ActFactory(
            b_conference=self.current_conference,
            performer=self.performer)
        data['theact-b_title'] = original.b_title
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The act has the same title")
