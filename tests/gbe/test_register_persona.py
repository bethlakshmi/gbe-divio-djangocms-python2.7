from django.test import TestCase
from django.test import Client
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    UserFactory,
    UserMessageFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    location,
    login_as,
)
from gbetext import default_create_persona_msg
from gbe.models import UserMessage
from django.core.files import File


class TestRegisterPersona(TestCase):
    '''Tests for index view'''
    view_name = 'persona_create'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.profile = ProfileFactory()
        ProfileFactory(user_object__username="admin_img")

    def submit_persona(self, image=None):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)

        data = {'performer_profile': self.profile.pk,
                'contact': self.profile.pk,
                'name': 'persona for %s' % self.profile.display_name,
                'homepage': 'foo.bar.com/~quux',
                'bio': 'bio bio bio',
                'experience': 3,
                'awards': 'Generic string here'}
        if image:
            data['upload_img'] = image
        persona_count = self.profile.personae.count()
        response = self.client.post(
            url,
            data,
            follow=True)
        return response, persona_count

    def test_register_persona_no_profile(self):
        login_as(UserFactory(), self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_register_persona_profile(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_persona_w_image(self):
        pic_filename = open("tests/gbe/gbe_pagebanner.png", 'r')
        picture = File(pic_filename)
        response, persona_count = self.submit_persona(picture)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "gbe_pagebanner.png")

    def test_register_persona_friendly_urls(self):
        response, persona_count = self.submit_persona()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, self.profile.personae.count()-persona_count)

    def test_register_persona_invalid_post(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)

        persona_count = self.profile.personae.count()
        response = self.client.post(
            url,
            data={'performer_profile': self.profile.pk,
                  'contact': self.profile.pk,
                  'name': '',
                  'homepage': 'foo.bar.com/~quux',
                  'bio': 'bio bio bio',
                  'experience': 3,
                  'awards': 'Generic string here'
                  })
        self.assertEqual(response.status_code, 200)
        assert "This field is required." in response.content

    def test_redirect(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.post(
            url + '?next=/troupe/create',
            data={'performer_profile': self.profile.pk,
                  'contact': self.profile.pk,
                  'name': 'persona name',
                  'homepage': 'foo.bar.com/~quux',
                  'bio': 'bio bio bio',
                  'experience': 3,
                  'awards': 'Generic string here',
                  },
            follow=True)
        assert response.status_code == 200
        self.assertRedirects(response,
                             reverse('troupe_create', urlconf='gbe.urls'))
        assert "Tell Us About Your Troupe" in response.content
        self.assertNotIn('<div class="alert alert-success">', response.content)

    def test_get(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')

        response = self.client.get(
            reverse('persona_create', urlconf='gbe.urls'),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Tell Us About Your Stage Persona" in response.content)

    def test_create_persona_make_message(self):
        response, persona_count = self.submit_persona()
        assert_alert_exists(
            response, 'success', 'Success', default_create_persona_msg)

    def test_create_persona_has_message(self):
        msg = UserMessageFactory(
            view='RegisterPersonaView',
            code='CREATE_PERSONA')
        response, persona_count = self.submit_persona()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
