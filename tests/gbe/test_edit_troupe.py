from django.test import TestCase
from django.core.urlresolvers import reverse
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
from gbetext import default_edit_troupe_msg
from gbe.models import UserMessage

# oddly, we can edit troupes even though we can't create them, and we can
# create combos but we can't edit them. This will have to be looked at.


class TestCreateTroupe(TestCase):
    '''Tests for edit_troupe view'''

    view_name = 'troupe_create'

    def setUp(self):
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Troupe'

    def test_create_troupe_no_performer(self):
        '''edit_troupe view, create flow
        '''
        login_as(UserFactory(), self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        expected_loc = '/update_profile?next=/troupe/create'
        self.assertEqual(location(response), expected_loc)

    def test_create_troupe_performer_exists(self):
        contact = PersonaFactory()
        login_as(contact.performer_profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.troupe_string)

    def test_create_troupe_no_inactive_users(self):
        contact = PersonaFactory()
        inactive = PersonaFactory(contact__user_object__is_active=False)
        login_as(contact.performer_profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(contact))
        self.assertNotContains(response, str(inactive))


class TestEditTroupe(TestCase):
    view_name = 'troupe_edit'

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

    def test_edit_as_member(self):
        '''edit_troupe view, edit flow success
        '''
        persona = PersonaFactory()
        troupe = TroupeFactory()
        troupe.membership.add(persona)
        troupe.save()
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(persona.performer_profile.profile, self)
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse(
                'troupe_view',
                urlconf='gbe.urls',
                args=[str(troupe.pk)]))

    def test_no_persona(self):
        profile = ProfileFactory()
        troupe = TroupeFactory()
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        request = self.factory.get('/troupe/edit/%d' % troupe.pk)
        login_as(profile, self)
        response = self.client.get(url)
        expected_loc = '/performer/create?next=/troupe/create'
        self.assertEqual(expected_loc, location(response))
        self.assertEqual(response.status_code, 302)

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
            view='EditTroupeView',
            code='UPDATE_TROUPE')
        response, data = self.submit_troupe()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
