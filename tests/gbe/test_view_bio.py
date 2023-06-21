from django.test import TestCase
from django.urls import reverse
from django.test import Client
from tests.factories.gbe_factories import (
    BioFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.functions.scheduler_functions import get_or_create_bio


class TestViewBio(TestCase):
    view_name = 'bio_view'

    '''Tests for view_troupe view'''
    def setUp(self):
        self.client = Client()

    def test_view_troupe(self):
        '''view_troupe view, success
        '''
        persona = BioFactory()
        contact = persona.contact
        troupe = BioFactory(contact=contact, multiple_performers=True)
        people = get_or_create_bio(troupe)
        url = reverse(self.view_name, args=[troupe.pk], urlconf='gbe.urls')
        login_as(contact, self)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, troupe.name)

    def test_no_profile(self):
        troupe = BioFactory(multiple_performers=True)
        people = get_or_create_bio(troupe)
        user = UserFactory()
        url = reverse(
            self.view_name,
            args=[troupe.pk],
            urlconf='gbe.urls')
        login_as(user, self)
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)

    def test_review_class_no_state_in_profile(self):
        troupe = BioFactory(multiple_performers=True)
        troupe.contact.state = ''
        troupe.contact.save()
        people = get_or_create_bio(troupe)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')

        login_as(troupe.contact, self)
        response = self.client.get(url)
        self.assertContains(response, 'No State Chosen')

    def test_view_performer_as_privileged_user(self):
        '''test with a performer, to make sure soloist also works
        '''
        persona = BioFactory()
        priv_profile = ProfileFactory()
        grant_privilege(priv_profile.user_object, 'Registrar')

        url = reverse(self.view_name,
                      args=[persona.pk],
                      urlconf='gbe.urls')
        login_as(priv_profile.user_object, self)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Performer")
        self.assertContains(response, persona.name)
        self.assertContains(response, persona.contact.user_object.email)

    def test_view_troupe_as_member(self):
        '''view_troupe view, success
        '''
        member = ProfileFactory()
        troupe = BioFactory(multiple_performers=True)
        people = get_or_create_bio(troupe)
        people.users.add(member.user_object)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(member.user_object, self)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Troupe")
        self.assertContains(response, troupe.name)
        self.assertContains(response, troupe.contact.user_object.email)
        self.assertContains(response, member.display_name)

    def test_view_troupe_as_random_person(self):
        '''view_troupe view, success
        '''
        persona = BioFactory()
        random = ProfileFactory()
        contact = persona.contact
        troupe = BioFactory(contact=contact, multiple_performers=True)
        people = get_or_create_bio(troupe)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(random.user_object, self)

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
