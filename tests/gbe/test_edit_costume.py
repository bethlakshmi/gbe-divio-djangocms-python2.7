from django.test import TestCase
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    CostumeFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    location,
)
from gbetext import (
    default_costume_submit_msg,
    default_costume_draft_msg
)
from gbe.models import UserMessage


class TestEditCostume(TestCase):
    '''Tests for edit_costume view'''
    view_name = 'costume_edit'

    # this test case should be unnecessary, since edit_costume should go away
    # for now, test it.

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()

    def get_costume_form(self, submit=False, invalid=False):
        picture = SimpleUploadedFile("file.jpg",
                                     "file_content",
                                     content_type="image/jpg")
        data = {'b_title': 'A costume',
                'creator': 'A creator',
                'b_description': 'pieces are listed',
                'active_use': True,
                'pieces': 10,
                'pasties': False,
                'dress_size': 10,
                'picture': picture,
                }
        if invalid:
            del(data['b_title'])
        if submit:
            data['submit'] = 1

        return data

    def post_edit_costume_submission(self):
        persona = PersonaFactory()
        costume = CostumeFactory(profile=persona.performer_profile,
                                 performer=persona)

        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form(submit=True)
        login_as(costume.profile, self)
        response = self.client.post(url, data=data, follow=True)
        return response

    def post_edit_costume_draft(self):
        persona = PersonaFactory()
        costume = CostumeFactory(profile=persona.performer_profile,
                                 performer=persona)

        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form(submit=False)
        login_as(costume.profile, self)
        response = self.client.post(url, data=data, follow=True)
        return response

    def test_edit_costume_no_costume(self):
        '''Should get 404 if no valid costume ID'''
        url = reverse(self.view_name,
                      args=[0],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_edit_costume_profile_is_not_contact(self):
        ''' Should get an error if the costume was not proposed by this user'''
        costume = CostumeFactory()
        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        login_as(PersonaFactory().performer_profile, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_edit_costume_no_profile(self):
        costume = CostumeFactory()
        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_costume_edit_post_form_not_valid(self):
        '''costume_edit, if form not valid, should return to edit'''
        costume = CostumeFactory()
        PersonaFactory(performer_profile=costume.profile,
                       contact=costume.profile)
        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form(invalid=True)
        login_as(costume.profile, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_edit_bid_post_no_submit(self):
        '''edit_costume, not submitting and no other problems,
        should redirect to home'''
        response = self.post_edit_costume_draft()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))

    def test_edit_bid_post_submit(self):
        '''edit_costume, not submitting and no other problems,
        should redirect to home'''
        response = self.post_edit_costume_submission()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))

    def test_edit_bid_post_invalid(self):
        '''edit_costume, not submitting and no other problems,
        should redirect to home'''
        persona = PersonaFactory()
        costume = CostumeFactory(profile=persona.performer_profile,
                                 performer=persona)

        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form(invalid=True)
        login_as(costume.profile, self)
        response = self.client.post(url, data=data)
        expected_string = "Costume Information"
        self.assertTrue(expected_string in response.content)
        self.assertEqual(response.status_code, 200)

    def test_submit_bid_post_invalid(self):
        '''edit_costume, not submitting and no other problems,
        should redirect to home'''
        persona = PersonaFactory()
        costume = CostumeFactory(profile=persona.performer_profile,
                                 performer=persona)

        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form(submit=True)
        data['b_title'] = ''
        data['b_description'] = ''
        login_as(costume.profile, self)
        response = self.client.post(url, data=data)
        self.assertContains(response, 'This field is required.', count=2)

    def test_edit_bid_not_post(self):
        '''edit_costume, not post, should take us to edit process'''
        persona = PersonaFactory()
        costume = CostumeFactory(profile=persona.performer_profile,
                                 performer=persona)
        url = reverse(self.view_name,
                      args=[costume.pk],
                      urlconf='gbe.urls')
        data = self.get_costume_form()
        login_as(costume.profile, self)
        response = self.client.get(url)
        expected_text = "Displaying a Costume"
        self.assertTrue(expected_text in response.content)
        self.assertContains(response, costume.b_description)

    def test_costume_submit_make_message(self):
        response = self.post_edit_costume_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_costume_submit_msg)

    def test_costume_draft_make_message(self):
        response = self.post_edit_costume_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_costume_draft_msg)

    def test_costume_submit_has_message(self):
        msg = UserMessageFactory(
            view='MakeCostumeView',
            code='SUBMIT_SUCCESS')
        response = self.post_edit_costume_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_costume_draft_has_message(self):
        msg = UserMessageFactory(
            view='MakeCostumeView',
            code='DRAFT_SUCCESS')
        response = self.post_edit_costume_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
