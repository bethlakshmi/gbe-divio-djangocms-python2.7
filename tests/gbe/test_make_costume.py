from django.test import TestCase
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    CostumeFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from gbe.models import Conference
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
)
from gbetext import (
    default_costume_submit_msg,
    default_costume_draft_msg
)


class TestMakeCostume(TestCase):

    @classmethod
    def setUpTestData(cls):
        Conference.objects.all().delete()
        cls.performer = PersonaFactory()
        cls.conference = ConferenceFactory(status='upcoming', 
                                           accepting_bids=True)

    def setUp(self):
        self.client = Client()

    def get_costume_form(self, submit=False, invalid=False):
        picture = SimpleUploadedFile("file.jpg",
                                     b"file_content",
                                     content_type="image/jpg")
        data = {'b_title': 'A costume',
                'creator': 'A creator',
                'b_description': 'pieces are listed',
                'active_use': True,
                'pieces': 10,
                'pasties': False,
                'dress_size': 10,
                'picture': picture,
                'phone': '111-222-3333',
                'first_name': 'Jane',
                'last_name': 'Smith',
                }
        if invalid:
            del(data['b_title'])
        if submit:
            data['submit'] = 1

        return data

    def check_subway_state(self, response, active_state="Apply"):
        self.assertContains(
            response,
            '<li class="progressbar_active">%s</li>' % active_state,
            html=True)
        self.assertNotContains(
                response,
                '<li class="progressbar_upcoming">Payment</li>',
                html=True)


class TestCreateCostume(TestMakeCostume):
    '''Tests for create_costume view'''
    view_name = 'costume_create'

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

    def test_post_no_profile(self):
        '''when user has no profile, should bounce out to /profile'''
        url = reverse(self.view_name, urlconf="gbe.urls")
        user = UserFactory()
        login_as(user, self)
        # this is class data, not act data, but won't get far enough to care
        data = self.get_costume_form()
        response = self.client.post(url, data=data, follow=True)
        self.assertRedirects(
            response,
            '%s?next=%s' % (
                reverse('profile_update', urlconf='gbe.urls'), url))

    def test_costume_bid_post_form_not_valid(self):
        '''costume_bid, if form not valid, should return to CostumeEditForm'''
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(PersonaFactory().contact, self)
        data = self.get_costume_form(invalid=True)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Displaying a Costume')
        self.check_subway_state(response)

    def test_costume_bid_post_with_submit(self):
        '''costume_bid, submitting and no other problems,
        should redirect to home'''
        response, data = self.post_costume_submission()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        self.assertContains(response, "Dashboard")
        self.assertContains(response, "(Click to view)")
        self.assertContains(response, data['b_title'])
        assert_alert_exists(
            response, 'success', 'Success', default_costume_submit_msg)

    def test_costume_bid_post_draft(self):
        '''costume_bid, submit draft and no other problems,
        should redirect to home'''
        response, data = self.post_costume_draft()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        self.assertContains(response, "Dashboard")
        self.assertContains(response, "(Click to edit)")
        self.assertContains(response, data['b_title'])
        assert_alert_exists(
            response, 'success', 'Success', default_costume_draft_msg)

    def test_costume_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Displaying a Costume')
        self.check_subway_state(response)

    def test_costume_bid_no_persona(self):
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse("persona-add", urlconf='gbe.urls', args=[0]) +
            "?next=/costume/create")
        self.check_subway_state(response, active_state="Create Bio")

    def test_costume_bid_post_invalid_form_no_submit(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        data = self.get_costume_form(submit=False, invalid=True)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Displaying a Costume')


class TestEditCostume(TestMakeCostume):
    '''Tests for edit_costume view'''
    view_name = 'costume_edit'

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
        '''Testing redirect from make_bid groundwork through own groundwork'''
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
        assert_alert_exists(
            response, 'success', 'Success', default_costume_draft_msg)

    def test_edit_bid_post_submit(self):
        '''edit_costume, not submitting and no other problems,
        should redirect to home'''
        response = self.post_edit_costume_submission()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'success', 'Success', default_costume_submit_msg)

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
        self.assertContains(response, expected_string)
        self.assertEqual(response.status_code, 200)
        self.check_subway_state(response)

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
        self.check_subway_state(response)

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
        self.assertContains(response, expected_text)
        self.assertContains(response, costume.b_description)
