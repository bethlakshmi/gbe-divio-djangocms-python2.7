from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    assert_alert_exists,
    make_act_app_purchase,
)
from gbetext import (
    default_act_draft_msg,
)
from gbe.models import (
    Conference,
    UserMessage,
)


class TestSummerAct(TestCase):
    '''Tests for create_act view'''
    create_name = 'summeract_create'
    edit_name = 'summeract_edit'

    def setUp(self):
        self.url = reverse(self.create_name, urlconf='gbe.urls')
        Conference.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()
        self.current_conference = ConferenceFactory(
            accepting_bids=True,
            act_style='summer')
        UserMessage.objects.all().delete()

    def get_act_form(self, submit=False, valid=True):

        form_dict = {'theact-shows_preferences': [4],
                     'theact-b_title': 'An act',
                     'theact-track_title': 'a track',
                     'theact-track_artist': 'an artist',
                     'theact-b_description': 'a description',
                     'theact-performer': self.performer.resourceitem_id,
                     'theact-act_duration': '1:00',
                     'theact-b_conference': self.current_conference.pk,
                     'theact-is_summer': True,
                     }
        if not valid:
            form_dict['theact-shows_preferences'] = [2]
        if not submit:
            form_dict['draft'] = True
        else:
            form_dict['submit'] = True
        return form_dict

    def post_paid_act_submission(self, act_form=None):
        if not act_form:
            act_form = self.get_act_form(submit=True)
        url = reverse(self.create_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        make_act_app_purchase(self.current_conference,
                              self.performer.performer_profile.user_object)
        response = self.client.post(url, data=act_form, follow=True)
        return response, act_form

    def post_edit_paid_act_draft(self):
        act = ActFactory(b_conference=self.current_conference)
        url = reverse(self.edit_name,
                      args=[act.pk],
                      urlconf="gbe.urls")
        login_as(act.performer.contact, self)
        response = self.client.post(url,
                                    self.get_act_form(),
                                    follow=True)
        return response

    def test_bid_act_get_with_persona(self):
        url = reverse(self.create_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        expected_string = 'Please also consider this act for GBE12'
        self.assertContains(response, expected_string)
        self.assertEqual(response.status_code, 200)

    def test_act_bid_post_form_not_valid(self):
        login_as(self.performer.performer_profile, self)
        url = reverse(self.create_name, urlconf='gbe.urls')
        data = self.get_act_form(submit=True, valid=False)
        response = self.client.post(url,
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Select a valid choice. 2 is not one of the available choices.')

    def test_act_bid_get_with_redirect(self):
        url = reverse("act_create", urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse(self.create_name, urlconf="gbe.urls"))

    def test_act_bid_get_with_redirect_other_way(self):
        url = reverse(self.create_name, urlconf='gbe.urls')
        self.current_conference.act_style = "normal"
        self.current_conference.save()
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse("act_create", urlconf="gbe.urls"))

    def test_act_submit_paid_act(self):
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View</a> act")
        self.assertContains(response, data['theact-b_title'])

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory(b_conference=self.current_conference)
        url = reverse(self.edit_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(act.performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Thanks for submitting an act for consideration at the Summer')

    def test_edit_bid_w_redirect(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory(b_conference=self.current_conference)
        url = reverse("act_edit",
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(act.performer.contact, self)
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse(self.edit_name, args=[act.pk], urlconf="gbe.urls"))

    def test_edit_bid_w_redirect_other_way(self):
        '''edit_bid, not post, should take us to edit process'''
        act = ActFactory()
        url = reverse(self.edit_name,
                      args=[act.pk],
                      urlconf="gbe.urls")

        login_as(act.performer.contact, self)
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse("act_edit", args=[act.pk], urlconf="gbe.urls"))

    def test_edit_act_draft_make_message(self):
        response = self.post_edit_paid_act_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_act_draft_msg)
