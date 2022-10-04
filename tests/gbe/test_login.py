import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import(
    ProfileFactory,
)


class TestIndex(TestCase):
    '''Tests for index view'''

    def setUp(self):
        self.client = Client()
        self.url = reverse('home', urlconf='gbe.urls')

        # User/Human setup
        self.profile = ProfileFactory(user_object__email="different",
                                      user_object__username="something")

    def test_login_w_email(self):
        '''Basic test of landing_page view
        '''
        self.profile.user_object.set_password('foo')
        self.profile.user_object.save()
        self.client.login(
            username=self.profile.user_object.email,
            email=self.profile.user_object.email,
            password='foo')
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, "Your Account")

    def test_bad_password_w_email(self):
        '''Basic test of landing_page view
        '''
        url = reverse('home', urlconf='gbe.urls')
        self.profile.user_object.set_password('foo')
        self.profile.user_object.save()
        self.client.login(
            username=self.profile.user_object.email,
            email=self.profile.user_object.email,
            password='crap')
        response = self.client.get(self.url, follow=True)
        self.assertNotContains(response, "Your Account")

    def test_bad_user_w_email(self):
        '''Basic test of landing_page view
        '''
        url = reverse('home', urlconf='gbe.urls')
        self.profile.user_object.set_password('foo')
        self.profile.user_object.save()
        self.client.login(
            username="notrealuser@crap.com",
            email=self.profile.user_object.email,
            password='foo')
        response = self.client.get(self.url, follow=True)
        self.assertNotContains(response, "Your Account")

    def test_no_user_w_email(self):
        '''Basic test of landing_page view
        '''
        url = reverse('home', urlconf='gbe.urls')
        self.profile.user_object.set_password('foo')
        self.profile.user_object.save()
        self.client.login(
            username=None,
            email=self.profile.user_object.email,
            password='foo')
        response = self.client.get(self.url, follow=True)
        self.assertNotContains(response, "Your Account")
