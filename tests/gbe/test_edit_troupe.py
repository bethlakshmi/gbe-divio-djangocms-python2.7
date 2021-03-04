from django.test import TestCase
from django.urls import reverse
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    TroupeFactory,
    UserFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    location
)
from gbetext import (
    default_edit_troupe_msg,
    no_persona_msg,
    no_profile_msg,
    troupe_header_text,
)
from gbe.models import UserMessage


class TestCreateTroupe(TestCase):
    '''Tests for edit_troupe view'''

    view_name = 'troupe-add'

    def setUp(self):
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Troupe'

    def test_create_troupe_no_persona(self):
        '''edit_troupe view, create flow
        '''
        user = ProfileFactory()
        login_as(user.user_object, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url, follow=True)
        expected_loc = '%s?next=%s' % (
            reverse('persona-add', urlconf="gbe.urls", args=[1]),
            url)
        self.assertRedirects(response, expected_loc)
        self.assertContains(response, no_persona_msg)

    def test_create_troupe_performer_exists(self):
        contact = PersonaFactory()
        login_as(contact.performer_profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.troupe_string)
        self.assertContains(response, troupe_header_text)

    def test_create_troupe_no_inactive_users(self):
        contact = PersonaFactory()
        inactive = PersonaFactory(contact__user_object__is_active=False)
        login_as(contact.performer_profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, str(inactive))


class TestEditTroupe(TestCase):
    view_name = 'troupe-update'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()

    def submit_troupe(self):
        persona = PersonaFactory()
        contact = persona.performer_profile
        troupe = TroupeFactory(contact=contact)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(contact.profile, self)
        data = {'contact': persona.performer_profile.pk,
                'name':  "New Troupe",
                'homepage': persona.homepage,
                'bio': "bio",
                'experience': 1,
                'awards': "many",
                'membership': [persona.pk]}
        response = self.client.post(
            url,
            data=data,
            follow=True
        )
        self.assertEqual(troupe.membership.first(), persona)
        return response, data

    def test_get_edit_troupe(self):
        '''edit_troupe view, edit flow success
        '''
        persona = PersonaFactory()
        contact = persona.performer_profile
        troupe = TroupeFactory(contact=contact)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(contact.profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tell Us About Your Troupe')

    def test_edit_wrong_user(self):
        '''edit_troupe view, edit flow success
        '''
        persona = PersonaFactory()
        troupe = TroupeFactory()
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(persona.performer_profile.profile, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_no_profile(self):
        troupe = TroupeFactory()
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        request = self.factory.get('/troupe/edit/%d' % troupe.pk)
        login_as(UserFactory(), self)
        response = self.client.get(url, follow=True)
        expected_loc = '%s?next=%s' % (
            reverse('profile_update', urlconf="gbe.urls"),
            url)
        self.assertRedirects(response, expected_loc)
        self.assertContains(response, no_profile_msg)

    def test_edit_troupe(self):
        '''edit_troupe view, edit flow success
        '''
        response, data = self.submit_troupe()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data['name'])
        self.assertContains(response, '(Click to edit)')

    def test_edit_troupe_bad_data(self):
        '''edit_troupe view, edit flow success
        '''
        persona = PersonaFactory()
        contact = persona.performer_profile
        troupe = TroupeFactory(contact=contact)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(contact.profile, self)
        data = {'contact': persona.performer_profile.pk,
                'name':  "New Troupe",
                'homepage': persona.homepage,
                'bio': "bio",
                'experience': 'bad',
                'awards': "many",
                'membership': [persona.pk]}
        response = self.client.post(
            url,
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tell Us About Your Troupe')
        expected_string = "Enter a whole number."
        self.assertContains(response, expected_string)

    def test_update_profile_make_message(self):
        response, data = self.submit_troupe()
        assert_alert_exists(
            response, 'success', 'Success', default_edit_troupe_msg)

    def test_update_profile_has_message(self):
        msg = UserMessageFactory(
            view='TroupeUpdate',
            code='SUCCESS')
        response, data = self.submit_troupe()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
