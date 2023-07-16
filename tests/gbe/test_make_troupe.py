from django.test import TestCase
from django.urls import reverse
from django.test import Client
from tests.factories.gbe_factories import (
    BioFactory,
    ProfileFactory,
    SocialLinkFactory,
    UserFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
)
from gbetext import (
    default_edit_troupe_msg,
    troupe_header_text,
)
from gbe_utils.text import no_profile_msg
from gbe.models import (
    SocialLink,
    UserMessage,
)
from scheduler.models import People
from tests.gbe.test_gbe import TestGBE
from tests.functions.scheduler_functions import get_or_create_bio


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


class TestTroupeCreate(TestGBE):
    '''Tests for edit_troupe view'''

    view_name = 'troupe-add'

    def setUp(self):
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Troupe'

    def test_create_troupe_performer_exists(self):
        contact = BioFactory()
        login_as(contact.contact, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.troupe_string)
        self.assertContains(response, troupe_header_text)
        self.assert_radio_state(response,
                                'pronouns_0',
                                'id_pronouns_0_2',
                                'they/them',
                                checked=True)
        self.assertNotContains(
            response,
            '<a href="#" data-toggle="modal" data-target="#DeleteModal" ' +
            'data-backdrop="true" class="btn gbe-btn-secondary">Delete</a>',
            html=True)

    def test_create_troupe_no_inactive_users(self):
        contact = BioFactory()
        inactive = BioFactory(contact__user_object__is_active=False)
        login_as(contact.contact, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, str(inactive))
        self.assertContains(response, 'Manage Troupe')
        self.assertContains(response, 'Tell Us About Your Troupe')
        for i in range(0, 5):
            self.assertContains(
                response,
                ('<input type="hidden" name="links-%d-id" id=' +
                 '"id_links-%d-id">') % (i, i),
                html=True)

    def test_create_troupe_post(self):
        msg = UserMessageFactory(
            view='TroupeCreate',
            code='SUCCESS')
        persona = BioFactory()
        contact = persona.contact
        other_member = ProfileFactory()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(contact, self)
        data = {'contact': persona.contact.pk,
                'name':  "New Troupe",
                'bio': "bio",
                'year_started': 2001,
                'awards': "many",
                'pronouns_0': '',
                'multiple_performers': True,
                'pronouns_1': 'custom/pronouns',
                'membership': [contact.pk, other_member.pk], }
        data.update(formset_data)
        response = self.client.post(
            url,
            data=data,
            follow=True
        )
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
        self.assertEquals(
            contact.bio_set.filter(multiple_performers=True).count(),
            1)
        troupe = contact.bio_set.filter(multiple_performers=True).first()
        self.assertTrue(
            People.objects.filter(class_name=troupe.__class__.__name__,
                                  class_id=troupe.pk).exists())


class TestTroupeEdit(TestCase):
    view_name = 'troupe-update'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()

    def submit_troupe(self, name=None):
        persona = BioFactory()
        contact = persona.contact
        troupe = BioFactory(multiple_performers=True, contact=contact)
        people = get_or_create_bio(troupe)
        link0 = SocialLinkFactory(bio=troupe)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(contact, self)
        data = {'contact': persona.contact.pk,
                'name':  name or "New Troupe",
                'bio': "bio",
                'year_started': 2001,
                'awards': "many",
                'pronouns_0': '',
                'multiple_performers': True,
                'pronouns_1': 'custom/pronouns',
                'membership': [contact.pk], }
        data.update(formset_data)
        data['links-0-id'] = link0.pk
        data['links-0-bio'] = troupe.pk
        data['links-INITIAL_FORMS'] = 1
        response = self.client.post(
            url,
            data=data,
            follow=True
        )
        self.assertTrue(people.users.filter(
            pk=contact.user_object.pk).exists())
        return response, data

    def test_get_edit_troupe(self):
        '''edit_troupe view, edit flow success
        '''
        persona = BioFactory()
        contact = persona.contact
        troupe = BioFactory(contact=contact, multiple_performers=True)
        people = get_or_create_bio(troupe)
        link0 = SocialLinkFactory(bio=troupe)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tell Us About Your Troupe')
        self.assertContains(
            response,
            '<a href="#" data-toggle="modal" data-target="#DeleteModal" ' +
            'data-backdrop="true" class="btn gbe-btn-secondary">Delete</a>',
            html=True)
        self.assertContains(
            response,
            ('<input type="hidden" name="links-0-id" id="id_links-0-id" ' +
             'value="%d">') % link0.pk,
            html=True)
        self.assertContains(
            response,
            '<input type="url" name="links-0-link" ' +
            'value="' + link0.link.replace('"', '&quot;') +
            '" placeholder="http://" style="width: 98%;box-sizing:' +
            'border-box" maxlength="200" id="id_links-0-link">',
            html=True)

    def test_edit_wrong_user(self):
        '''edit_troupe view, edit flow success
        '''
        persona = BioFactory()
        troupe = BioFactory(multiple_performers=True)
        people = get_or_create_bio(troupe)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(persona.contact, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_no_profile(self):
        troupe = BioFactory(multiple_performers=True)
        people = get_or_create_bio(troupe)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url, follow=True)
        expected_loc = '%s?next=%s' % (
            reverse('profile_update', urlconf="gbe.urls"),
            url)
        self.assertRedirects(response, expected_loc)
        self.assertContains(response, no_profile_msg)

    def test_edit_troupe(self):
        ''' successful edit, and social link is removed
        '''
        name = '"extra quotes"'
        response, data = self.submit_troupe(name=name)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tell Us About Your Troupe')
        self.assertContains(
            response,
            '<input type="text" name="name" value="extra quotes" ' +
            'maxlength="100" id="id_name">',
            html=True)
        self.assertContains(response, name.strip('\"\''))
        self.assertFalse(SocialLink.objects.filter(
            pk=data['links-0-id']).exists())
        assert_alert_exists(
            response, 'success', 'Success', default_edit_troupe_msg)

    def test_edit_troupe_bad_data(self):
        '''edit_troupe view, edit flow success
        '''
        persona = BioFactory()
        contact = persona.contact
        troupe = BioFactory(contact=contact, multiple_performers=True)
        people = get_or_create_bio(troupe)
        url = reverse(self.view_name,
                      args=[troupe.pk],
                      urlconf='gbe.urls')
        login_as(contact, self)
        data = {'contact': persona.contact.pk,
                'name':  "New Troupe",
                'bio': "bio",
                'year_started': 'bad',
                'awards': "many",
                'membership': [contact.pk]}
        data.update(formset_data)
        response = self.client.post(
            url,
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tell Us About Your Troupe')
        expected_string = "Enter a whole number."
        self.assertContains(response, expected_string)

    def test_update_profile_has_message(self):
        msg = UserMessageFactory(
            view='TroupeUpdate',
            code='SUCCESS')
        response, data = self.submit_troupe()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
