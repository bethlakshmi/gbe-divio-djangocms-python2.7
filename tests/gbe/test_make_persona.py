from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    UserFactory,
    UserMessageFactory,
    PersonaFactory,
    ProfileFactory,
    SocialLinkFactory,
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

formset_data = {
    'links-0-social_network': '',
    'links-0-order': 1,
    'links-0-link': '',
    'links-0-username': '',
    'links-1-social_network': '',
    'links-1-order': 2,
    'links-1-link': '',
    'links-1-username': '',
    'links-2-social_network': '',
    'links-2-order': 3,
    'links-2-link': '',
    'links-2-username': '',
    'links-3-social_network': '',
    'links-3-order': 4,
    'links-3-link': '',
    'links-3-username': '',
    'links-4-social_network': '',
    'links-4-order': 5,
    'links-4-link': '',
    'links-4-username': '',
    'links-TOTAL_FORMS': 5,
    'links-INITIAL_FORMS': 0,
    'links-MIN_NUM_FORMS': 0,
    'links-MAX_NUM_FORMS': 5,
}


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

        data = {'performer_profile': self.profile.pk,
                'contact': self.profile.pk,
                'name': name or 'persona for %s' % self.profile.display_name,
                'bio': 'bio bio bio',
                'year_started': 2003,
                'awards': 'Generic string here',
                }
        data.update(formset_data)
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
        for i in range(0, 5):
            self.assertContains(
                response,
                ('<input type="hidden" name="links-%d-id" id=' +
                 '"id_links-%d-id">') % (i, i),
                html=True)

    def test_register_persona_w_image(self):
        pic_filename = open("tests/gbe/gbe_pagebanner.png", 'rb')
        response, persona_count = self.submit_persona(pic_filename)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "gbe_pagebanner.png")
        self.assertEqual(1, self.profile.personae.count()-persona_count)

    def test_register_persona_invalid_post(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[1])
        response = self.client.get(url)
        data = {'performer_profile': self.profile.pk,
                'contact': self.profile.pk,
                'name': '',
                'bio': 'bio bio bio',
                'year_started': 2003,
                'awards': 'Generic string here'}
        data.update(formset_data)
        persona_count = self.profile.personae.count()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_redirect(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[1])
        data = {'performer_profile': self.profile.pk,
                'contact': self.profile.pk,
                'name': 'persona name',
                'bio': 'bio bio bio',
                'year_started': 2003,
                'awards': 'Generic string here'}
        data.update(formset_data)
        response = self.client.post(
            url + '?next=%s' % reverse("troupe-add", urlconf='gbe.urls'),
            data,
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
        self.link0 = SocialLinkFactory(performer=self.persona)
        self.link1 = SocialLinkFactory(
            performer=self.persona,
            order=2,
            link='',
            username='username',
            social_network='Paypal')

    def submit_persona(self, image=None, delete_image=False):
        login_as(self.persona.performer_profile, self)
        new_name = "Fifi"
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id, 1])
        data = {'performer_profile': self.persona.performer_profile.pk,
                'contact': self.persona.performer_profile.pk,
                'name': new_name,
                'bio': "bio",
                'year_started': 2001,
                'awards': "many"}
        data.update(formset_data)
        data['links-0-id'] = self.link0.pk
        data['links-1-id'] = self.link1.pk
        data['links-0-performer'] = self.persona.pk
        data['links-1-performer'] = self.persona.pk
        data['links-INITIAL_FORMS'] = 2
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
        self.assertContains(
            response,
            ('<input type="hidden" name="links-0-id" id="id_links-0-id" ' +
             'value="%d">') % self.link0.pk,
            html=True)
        self.assertContains(
            response,
            '<input type="url" name="links-0-link" ' +
            'value="' + self.link0.link.replace('"', '&quot;') +
            '" placeholder="http://" style="width: 98%;box-sizing:' +
            'border-box" maxlength="200" id="id_links-0-link">',
            html=True)
        self.assertContains(
            response,
            ('<input type="hidden" name="links-1-id" id=' +
             '"id_links-1-id" value="%d">') % self.link1.pk,
            html=True)
        self.assertContains(
            response,
            ('<input type="text" name="links-1-username" value="%s" ' +
             'placeholder="yourusername" maxlength="100" ' +
             'id="id_links-1-username">') % self.link1.username,
            html=True)
        for i in range(2, 5):
            self.assertContains(
                response,
                ('<input type="hidden" name="links-%d-id" id=' +
                 '"id_links-%d-id">') % (i, i),
                html=True)
        for i in range(0, 5):
            self.assertContains(
                response,
                ('<input type="hidden" name="links-%d-performer" id="id_' +
                 'links-%d-performer" value="%d">') % (i, i, self.persona.pk),
                html=True)

    def test_edit_persona_load_img(self):
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
        ''' - image is changed
            - the data sent should erase both links
        '''
        ProfileFactory(user_object__username="admin_img")
        pic_filename = open("tests/gbe/gbe_pagebanner.png", 'rb')
        response, new_name = self.submit_persona(pic_filename)
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(str(persona_reloaded.img), "gbe_pagebanner.png")
        self.assertEqual(persona_reloaded.links.count(), 0)
        assert_alert_exists(
            response, 'success', 'Success', default_edit_persona_msg)

    def test_change_image_foreign_char(self):
        '''
         - compatible w. foreign character
         - links are changed & new one is made
         - checks that order is resorted in sequential order
        '''
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
                'bio': "bio",
                'year_started': 2001,
                'awards': "many",
                'upload_img': pic_filename,
                'links-0-performer': self.persona.pk,
                'links-1-performer': self.persona.pk,
                'links-2-performer': self.persona.pk,
                }
        data.update(formset_data)
        data['links-0-id'] = self.link0.pk
        data['links-1-id'] = self.link1.pk
        data['links-0-social_network'] = 'Venmo'
        data['links-0-username'] = 'venmouser'
        data['links-1-order'] = 4
        data['links-1-social_network'] = self.link1.social_network
        data['links-1-username'] = self.link1.username
        data['links-2-social_network'] = 'Facebook'
        data['links-2-link'] = 'http://www.facebook.com/somepage'
        data['links-0-performer'] = self.persona.pk
        data['links-1-performer'] = self.persona.pk
        data['links-2-performer'] = self.persona.pk
        data['links-INITIAL_FORMS'] = 2
        response = self.client.post(
            url,
            data,
            follow=True
        )
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(str(persona_reloaded.img), "gbe_pagebanner.png")
        reload_link0 = persona_reloaded.links.get(pk=self.link0.pk)
        reload_link1 = persona_reloaded.links.get(pk=self.link1.pk)
        reload_link2 = persona_reloaded.links.latest('pk')
        self.assertEqual(reload_link0.social_network, 'Venmo')
        self.assertEqual(reload_link0.username, 'venmouser')
        self.assertEqual(reload_link1.social_network,
                         self.link1.social_network)
        self.assertEqual(reload_link1.username, self.link1.username)
        self.assertEqual(reload_link1.order, 3)
        self.assertEqual(reload_link2.order, 2)
        self.assertEqual(reload_link2.social_network, 'Facebook')
        self.assertEqual(reload_link2.link, 'http://www.facebook.com/somepage')
        assert_alert_exists(
            response, 'success', 'Success', default_edit_persona_msg)

    def test_edit_persona_remove_image(self):
        set_image(self.persona)
        self.assertEqual(str(self.persona.img), "gbe_pagebanner.png")
        response, new_name = self.submit_persona(delete_image=True)
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(persona_reloaded.img, None)
        assert_alert_exists(
            response, 'success', 'Success', default_edit_persona_msg)

    def test_edit_persona_invalid_post(self):
        login_as(self.persona.performer_profile, self)
        old_name = self.persona.name
        new_name = "Fifi"
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id, 1])
        data = {'performer_profile': self.persona.pk,
                'contact': self.persona.pk,
                'name': new_name,
                'bio': "bio",
                'year_started': 2001,
                'awards': "many"}
        data.update(formset_data)
        response = self.client.post(url, data=data)
        self.assertContains(response, self.expected_string)
        persona_reloaded = Persona.objects.get(pk=self.persona.pk)
        self.assertEqual(persona_reloaded.name, old_name)

    def test_edit_persona_delete_link(self):
        login_as(self.persona.performer_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id, 1])
        data = {'performer_profile': self.persona.performer_profile.pk,
                'contact': self.persona.performer_profile.pk,
                'name': "Fifi",
                'bio': "bio",
                'year_started': 2001,
                'awards': "many"}
        data.update(formset_data)
        data['links-0-id'] = self.link0.pk
        data['links-1-id'] = self.link1.pk
        data['links-1-social_network'] = self.link1.social_network
        data['links-1-username'] = self.link1.username
        data['links-0-performer'] = self.persona.pk
        data['links-1-performer'] = self.persona.pk
        data['links-INITIAL_FORMS'] = 2
        data['links-0-DELETE'] = 1
        response = self.client.post(
            url,
            data,
            follow=True
        )
        self.assertEqual(self.persona.links.count(), 1)

    def test_edit_persona_invalid_links(self):
        login_as(self.persona.performer_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.persona.resourceitem_id, 1])
        data = {'performer_profile': self.persona.performer_profile.pk,
                'contact': self.persona.performer_profile.pk,
                'name': "Fifi",
                'bio': "bio",
                'year_started': 2001,
                'awards': "many"}
        data.update(formset_data)
        data['links-0-id'] = self.link0.pk
        data['links-1-id'] = self.link1.pk
        data['links-0-social_network'] = 'Venmo'
        data['links-1-social_network'] = 'Website'
        data['links-0-performer'] = self.persona.pk
        data['links-1-performer'] = self.persona.pk
        data['links-INITIAL_FORMS'] = 2
        response = self.client.post(
            url,
            data,
            follow=True
        )
        self.assertContains(response, self.expected_string)
        self.assertContains(response, "This field is required.", 2)

    def test_edit_persona_has_message(self):
        msg = UserMessageFactory(
            view='PersonaUpdate',
            code='SUCCESS')
        response, new_name = self.submit_persona()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
