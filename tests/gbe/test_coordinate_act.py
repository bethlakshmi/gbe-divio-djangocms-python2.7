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
    grant_privilege,
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
    act_coord_instruct,
)
from gbe.models import (
    Conference,
    UserMessage,
)
from tests.functions.ticketing_functions import setup_fees
from ticketing.models import Transaction
from datetime import (
    datetime,
    timedelta,
)


class TestCoordinateAct(TestCase):
    '''Tests for create_act view'''
    view_name = 'act_coord_create'

    def setUp(self):
        self.url = reverse(self.view_name, urlconf='gbe.urls')
        Conference.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.current_conference = ConferenceFactory(accepting_bids=True)
        UserMessage.objects.all().delete()
        self.privileged_user = ProfileFactory.create().user_object
        grant_privilege(self.privileged_user,
                        'Act Coordinator',
                        'assign_act')

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

    def post_act_submission(self, act_form=None):
        if not act_form:
            act_form = self.get_act_form()
        url = reverse(self.view_name, urlconf='gbe.urls')
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
        data = self.get_act_form(submit=True, valid=False)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Act for Coordinator")
        self.assertContains(response, "This field is required.")

    def test_act_submit_act_succeed(self):
        tickets = setup_fees(self.current_conference, is_act=True)
        response, data = self.post_act_submission()
        print(response.content)
        just_made = self.performer.acts.all().first()
        self.assertRedirects(response, reverse('act_review',
                                               urlconf="gbe.urls",
                                               args=[just_made.id]))
        self.assertContains(response, just_made.title)
        self.assertRedirects(response, reverse('act_review',
                                               urlconf="gbe.urls",
                                               args=[just_made.id]))
        assert_alert_exists(
            response, 'success', 'Success', default_act_submit_msg)

    def test_act_submit_act_no_viable_ticket(self):
        response, data = self.post_act_submission()
        print(response.content)
        just_made = self.performer.acts.all().first()
        self.assertRedirects(response, reverse('act_review',
                                               urlconf="gbe.urls",
                                               args=[just_made.id]))
        self.assertContains(response, just_made.title)
        self.assertRedirects(response, reverse('act_review',
                                               urlconf="gbe.urls",
                                               args=[just_made.id]))
        assert_alert_exists(
            response, 'success', 'Success', default_act_submit_msg)

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
        self.assertContains(
            response, 
            "The act has the same title")
