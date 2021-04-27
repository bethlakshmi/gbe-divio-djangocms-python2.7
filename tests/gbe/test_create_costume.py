from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from tests.factories.gbe_factories import(
    PersonaFactory,
    ProfileFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    current_conference,
    login_as,
)
from gbetext import (
    default_costume_submit_msg,
    default_costume_draft_msg
)
from gbe.models import (
    Conference,
    UserMessage
)


class TestCreateCostume(TestCase):
    '''Tests for edit_costume view'''
    view_name = 'costume_create'

    def setUp(self):
        Conference.objects.all().delete()
        UserMessage.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        current_conference()

    def get_costume_form(self, submit=False, invalid=False):
        picture = SimpleUploadedFile("file.jpg",
                                     b"file_content",
                                     content_type="image/jpg")
        form = {'b_title': 'A costume',
                'creator': 'A creator',
                'b_description': 'pieces are listed',
                'active_use': True,
                'pieces': 10,
                'pasties': False,
                'dress_size': 10,
                'picture': picture,
                }
        if submit:
            form['submit'] = 1
        if invalid:
            del(form['b_title'])
        return form

    def post_costume_submission(self):
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(PersonaFactory().contact, self)
        data = self.get_costume_form(submit=True)
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def post_costume_draft(self):
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(PersonaFactory().contact, self)
        data = self.get_costume_form()
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def test_costume_bid_post_form_not_valid(self):
        '''costume_bid, if form not valid, should return to CostumeEditForm'''
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(PersonaFactory().contact, self)
        data = self.get_costume_form(invalid=True)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Displaying a Costume')

    def test_costume_bid_post_with_submit(self):
        '''costume_bid, submitting and no other problems,
        should redirect to home'''
        response, data = self.post_costume_submission()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        self.assertContains(response, "Your Account")
        self.assertContains(response, "(Click to view)")
        self.assertContains(response, data['b_title'])

    def test_costume_bid_post_draft(self):
        '''costume_bid, submit draft and no other problems,
        should redirect to home'''
        response, data = self.post_costume_draft()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        self.assertContains(response, "Your Account")
        self.assertContains(response, "(Click to edit)")
        self.assertContains(response, data['b_title'])

    def test_costume_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Displaying a Costume')

    def test_costume_bid_no_persona(self):
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_costume_bid_post_invalid_form_no_submit(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        data = self.get_costume_form(submit=False, invalid=True)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Displaying a Costume')

    def test_costume_submit_make_message(self):
        response, data = self.post_costume_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_costume_submit_msg)

    def test_costume_draft_make_message(self):
        response, data = self.post_costume_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_costume_draft_msg)

    def test_costume_submit_has_message(self):
        msg = UserMessageFactory(
            view='MakeCostumeView',
            code='SUBMIT_SUCCESS')
        response, data = self.post_costume_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_costume_draft_has_message(self):
        msg = UserMessageFactory(
            view='MakeCostumeView',
            code='DRAFT_SUCCESS')
        response, data = self.post_costume_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
