from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    UserFactory,
    UserMessageFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    set_image,
)
from gbetext import (
    default_create_persona_msg,
    default_edit_persona_msg,
)
from gbe.models import (
    Persona,
    UserMessage,
)


class TestPersonaCreate(TestCase):
    '''Tests for index view'''
    view_name = 'persona-add'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.profile = ProfileFactory()
        ProfileFactory(user_object__username="admin_img")

    def submit_persona(self, image=None, name=None):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[1])
        response = self.client.get(url)

        data = {'performer_profile': self.profile.pk,
                'contact': self.profile.pk,
                'name': name or 'persona for %s' % self.profile.display_name,
                'homepage': 'foo.bar.com/~quux',
                'bio': 'bio bio bio',
                'year_started': 2003,
                'awards': 'Generic string here'}
        if image:
            data['upload_img'] = image
        persona_count = self.profile.personae.count()
        response = self.client.post(
            url,
            data,
            follow=True)
        return response, persona_count

    def test_register_persona_profile(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            '<a href="#" data-toggle="modal" data-target="#DeleteModal" ' +
            'data-backdrop="true" class="btn gbe-btn-secondary">Delete</a>',
            html=True)

    def test_register_persona_w_image(self):
        pic_filename = open("tests/gbe/gbe_pagebanner.png", 'rb')
        response, persona_count = self.submit_persona(pic_filename)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "gbe_pagebanner.png")

    def test_register_persona_friendly_urls(self):
        response, persona_count = self.submit_persona()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, self.profile.personae.count()-persona_count)

    def test_register_persona_invalid_post(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[1])
        response = self.client.get(url)

        persona_count = self.profile.personae.count()
        response = self.client.post(
            url,
            data={'performer_profile': self.profile.pk,
                  'contact': self.profile.pk,
                  'name': '',
                  'homepage': 'foo.bar.com/~quux',
                  'bio': 'bio bio bio',
                  'year_started': 2003,
                  'awards': 'Generic string here'
                  })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_redirect(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[1])
        response = self.client.post(
            url + '?next=%s' % reverse("troupe-add", urlconf='gbe.urls'),
            data={'performer_profile': self.profile.pk,
                  'contact': self.profile.pk,
                  'name': 'persona name',
                  'homepage': 'foo.bar.com/~quux',
                  'bio': 'bio bio bio',
                  'year_started': 2003,
                  'awards': 'Generic string here',
                  },
            follow=True)
        assert response.status_code == 200
        self.assertRedirects(response,
                             reverse('troupe-add', urlconf='gbe.urls'))
        self.assertContains(response, "Tell Us About Your Troupe")
        self.assertNotContains(response, '<div class="alert alert-success">')

    def test_get(self):
        login_as(self.profile, self)
        response = self.client.get(
            reverse('persona-add', urlconf='gbe.urls', args=[1]),
        )
        self.assertContains(response, "Tell Us About Your Stage Persona")
        self.assertContains(response, "Create Troupe")
        self.assertContains(response,
                            reverse("troupe-add", urlconf="gbe.urls"))

    def test_get_no_troupe(self):
        login_as(self.profile, self)
        response = self.client.get(
            reverse('persona-add', urlconf='gbe.urls', args=[0]),
        )
        self.assertContains(response, "Tell Us About Your Stage Persona")
        self.assertNotContains(response, "Create Troupe")
        self.assertNotContains(response,
                               reverse("troupe-add", urlconf="gbe.urls"))

    def test_create_persona_make_message(self):
        name = '"extra quotes"'
        response, persona_count = self.submit_persona(name=name)
        assert_alert_exists(
            response, 'success', 'Success', default_create_persona_msg)
        self.assertNotContains(response, name)
        self.assertContains(response, name.strip('\"\''))

    def test_create_persona_has_message(self):
        msg = UserMessageFactory(
            view='PersonaCreate',
            code='SUCCESS')
        response, persona_count = self.submit_persona()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)


class TestPersonaEdit(TestCase):
    view_name = 'persona-update'

    '''Tests for edit_persona view'''
    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.expected_string = 'Tell Us About Your Stage Persona'
        self.persona = PersonaFactory()

    def submit_persona(self, image=None, delete_image=False):
        login_as(self.persona.performer_profile, self)
        old_name = self.persona.name
        new_name = "Fifi"
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id, 1])
        data = {'performer_profile': self.persona.performer_profile.pk,
                'contact': self.persona.performer_profile.pk,
                'name': new_name,
                'homepage': self.persona.homepage,
                'bio': "bio",
                'year_started': 2001,
                'awards': "many"}
        if image:
            data['upload_img'] = image
        if delete_image:
            data['upload_img-clear'] = True

        response = self.client.post(
            url,
            data,
            follow=True
        )
        return response, new_name

    def test_edit_persona(self):
        '''edit_troupe view, create flow
        '''
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id, 0])
        login_as(self.persona.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.expected_string)
        self.assertNotContains(response, "Create Troupe")
        self.assertContains(
            response,
            '<a href="#" data-toggle="modal" data-target="#DeleteModal" ' +
            'data-backdrop="true" class="btn gbe-btn-secondary">Delete</a>',
            html=True)
        self.assertContains(
            response,
            reverse("performer-delete",
                    urlconf="gbe.urls",
                    args=[self.persona.pk]))

    def test_edit_persona_load_img(self):
        '''edit_troupe view, create flow
        '''
        set_image(self.persona)

        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id, 1])
        login_as(self.persona.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.persona.img.url)
        self.assertContains(response, "Create Troupe")

    def test_wrong_profile(self):
        viewer = ProfileFactory()
        url = (reverse(self.view_name,
                       urlconf="gbe.urls",
                       args=[self.persona.pk, 1]))
        login_as(viewer, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_persona_change_stage_name(self):
        response, new_name = self.submit_persona()
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(persona_reloaded.name, new_name)

    def test_edit_persona_change_image(self):
        ProfileFactory(user_object__username="admin_img")
        pic_filename = open("tests/gbe/gbe_pagebanner.png", 'rb')

        response, new_name = self.submit_persona(pic_filename)
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(str(persona_reloaded.img), "gbe_pagebanner.png")

    def test_change_image_foreign_char(self):
        ProfileFactory(user_object__username="admin_img")
        pic_filename = open("tests/gbe/gbe_pagebanner.png", 'rb')

        login_as(self.persona.performer_profile, self)
        new_name = "Bitsy Brûlée"
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id, 0])
        data = {'performer_profile': self.persona.performer_profile.pk,
                'contact': self.persona.performer_profile.pk,
                'name': new_name,
                'homepage': self.persona.homepage,
                'bio': "bio",
                'year_started': 2001,
                'awards': "many",
                'upload_img': pic_filename}

        response = self.client.post(
            url,
            data,
            follow=True
        )
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(str(persona_reloaded.img), "gbe_pagebanner.png")

    def test_edit_persona_remove_image(self):
        set_image(self.persona)
        self.assertEqual(str(self.persona.img), "gbe_pagebanner.png")
        response, new_name = self.submit_persona(delete_image=True)
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(persona_reloaded.img, None)

    def test_edit_persona_invalid_post(self):
        login_as(self.persona.performer_profile, self)
        old_name = self.persona.name
        new_name = "Fifi"
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id, 1])
        response = self.client.post(
            url,
            data={'performer_profile': self.persona.pk,
                  'contact': self.persona.pk,
                  'name': new_name,
                  'homepage': self.persona.homepage,
                  'bio': "bio",
                  'year_started': 2001,
                  'awards': "many"}
        )
        self.assertContains(response, self.expected_string)
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(persona_reloaded.name, old_name)

    def test_edit_persona_make_message(self):
        response, new_name = self.submit_persona()
        assert_alert_exists(
            response, 'success', 'Success', default_edit_persona_msg)

    def test_edit_persona_has_message(self):
        msg = UserMessageFactory(
            view='PersonaUpdate',
            code='SUCCESS')
        response, new_name = self.submit_persona()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
