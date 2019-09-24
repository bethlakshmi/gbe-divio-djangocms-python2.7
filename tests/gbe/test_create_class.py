from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    UserMessageFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    location,
    login_as,
)
from gbetext import (
    default_class_submit_msg,
    default_class_draft_msg
)
from gbe.models import (
    Conference,
    UserMessage
)


class TestCreateClass(TestCase):
    '''Tests for create_class view'''
    view_name = 'class_create'

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()
        self.conference = ConferenceFactory(accepting_bids=True)
        UserMessage.objects.all().delete()

    def get_class_form(self,
                       submit=False,
                       invalid=False,
                       incomplete=False):
        data = {'theclass-teacher': self.performer.pk,
                'theclass-b_title': 'A class',
                'theclass-b_description': 'a description',
                'theclass-length_minutes': 60,
                'theclass-maximum_enrollment': 20,
                'theclass-fee': 0,
                'theclass-schedule_constraints': ['0'],
                }
        if submit:
            data['submit'] = 1
        if invalid:
            del(data['theclass-b_title'])
        if incomplete:
            data['theclass-b_title'] = ''
        return data

    def post_bid(self, submit=True):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        data = self.get_class_form(submit=submit)
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def test_bid_class_no_personae(self):
        '''class_bid, when profile has no personae,
        should redirect to persona_create'''
        profile = ProfileFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(
            url,
            follow=True)
        redirect = (('http://testserver/performer/create'
                     '?next=/class/create',
                     302))
        nt.assert_true(redirect in response.redirect_chain)
        expected_string = "Tell Us About Your Stage Persona"
        nt.assert_true(expected_string in response.content)
        nt.assert_equal(response.status_code, 200)

    def test_bid_class_no_personae(self):
        '''class_bid, when profile has no personae,
        should redirect to persona_create'''
        profile = ProfileFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(
            url,
            follow=True)
        redirect = ('http://testserver/performer/create?next=/class/create',
                    302)
        assert redirect in response.redirect_chain
        title = '<h2 class="subtitle">Tell Us About Your Stage Persona</h2>'
        assert title in response.content
        assert response.status_code == 200

    def test_class_bid_post_with_submit(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_bid(submit=True)
        self.assertEqual(response.status_code, 200)
        assert data['theclass-b_title'] in response.content
        # stricter test required here

    def test_class_bid_post_with_submit_incomplete(self):
        '''class_bid, submit, incomplete form'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        data = self.get_class_form(submit=True, invalid=True)
        user = self.performer.performer_profile.user_object
        login_as(user, self)
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        expected_string = "This field is required"
        self.assertTrue(expected_string in response.content)

    def test_class_bid_post_no_submit(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_bid(submit=False)
        self.assertEqual(200, response.status_code)
        assert 'Profile View' in response.content
        assert data['theclass-b_title'] in response.content

    def test_class_bid_post_invalid_form_no_submit(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        other_performer = PersonaFactory()
        other_profile = other_performer.performer_profile
        login_as(self.performer.performer_profile, self)
        data = self.get_class_form(submit=False, invalid=True)
        data['theclass-teacher'] = other_performer.pk
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue('Submit a Class' in response.content)
        self.assertFalse(other_performer.name in response.content)
        current_user_selection = '<option value="%d">%s</option>'
        persona_id = self.performer.pk
        selection_string = current_user_selection % (persona_id,
                                                     self.performer.name)
        self.assertTrue(selection_string in response.content)

    def test_class_bid_verify_info_popup_text(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            'We will do our best to accommodate' in response.content)

    def test_class_bid_verify_avoided_constraints(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('I Would Prefer to Avoid' in response.content)

    def test_class_submit_make_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_bid(submit=True)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_class_submit_msg)

    def test_class_submit_conflict_times(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        data = self.get_class_form(submit=True)
        data['theclass-avoided_constraints'] = ['0']
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        print response.content
        self.assertContains(
            response, "Available times conflict with unavailable times.  " +
            "Conflicts are: Friday Afternoon")

    def test_class_draft_make_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_bid(submit=False)
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_class_draft_msg)

    def test_class_submit_has_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        msg = UserMessageFactory(
            view='MakeClassView',
            code='SUBMIT_SUCCESS')
        response, data = self.post_bid(submit=True)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_class_draft_has_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        msg = UserMessageFactory(
            view='MakeClassView',
            code='DRAFT_SUCCESS')
        response, data = self.post_bid(submit=False)
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
