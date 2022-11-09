from django.test import TestCase
from django.urls import reverse
from django.test import Client
from gbe.views import ViewTroupeView
from tests.factories.gbe_factories import (
    TroupeFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestViewTroupe(TestCase):
    '''Tests for view_troupe view'''
    def setUp(self):
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Troupe'

    def test_view_troupe(self):
        '''view_troupe view, success
        '''
        persona = PersonaFactory()
        contact = persona.performer_profile
        troupe = TroupeFactory(contact=contact)
        url = reverse('troupe_view',
                      args=[troupe.resourceitem_id],
                      urlconf='gbe.urls')
        login_as(contact.profile.user_object, self)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, troupe.name)

    def test_no_profile(self):
        troupe = TroupeFactory()
        user = UserFactory()
        url = reverse(
            "troupe_view",
            args=[troupe.resourceitem_id],
            urlconf='gbe.urls')
        login_as(user, self)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_review_class_no_state_in_profile(self):
        troupe = TroupeFactory()
        troupe.contact.state = ''
        troupe.contact.save()
        url = reverse('troupe_view',
                      args=[troupe.resourceitem_id],
                      urlconf='gbe.urls')

        login_as(troupe.contact.profile.user_object, self)
        response = self.client.get(url)
        self.assertContains(response, 'No State Chosen')

    def test_view_troupe_as_privileged_user(self):
        '''view_troupe view, success
        '''
        persona = PersonaFactory()
        contact = persona.performer_profile
        troupe = TroupeFactory(contact=contact)
        priv_profile = ProfileFactory()
        grant_privilege(priv_profile.user_object, 'Registrar')

        url = reverse('troupe_view',
                      args=[troupe.resourceitem_id],
                      urlconf='gbe.urls')
        login_as(priv_profile.user_object, self)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, troupe.name)
        self.assertContains(response, troupe.contact.user_object.email)

    def test_view_troupe_as_member(self):
        '''view_troupe view, success
        '''
        persona = PersonaFactory()
        member = PersonaFactory()
        contact = persona.performer_profile
        troupe = TroupeFactory(contact=contact)
        troupe.membership.add(member)
        troupe.save()
        url = reverse('troupe_view',
                      args=[troupe.resourceitem_id],
                      urlconf='gbe.urls')
        login_as(member.performer_profile.user_object, self)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, troupe.name)
        self.assertContains(response, troupe.contact.user_object.email)
        self.assertContains(response, member.name)

    def test_view_troupe_as_random_person(self):
        '''view_troupe view, success
        '''
        persona = PersonaFactory()
        random = ProfileFactory()
        contact = persona.performer_profile
        troupe = TroupeFactory(contact=contact)
        url = reverse('troupe_view',
                      args=[troupe.resourceitem_id],
                      urlconf='gbe.urls')
        login_as(random.user_object, self)

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
