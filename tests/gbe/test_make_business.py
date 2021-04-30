from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    UserFactory,
    UserMessageFactory,
    BusinessFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    set_image,
)
from gbetext import (
    default_create_business_msg,
    default_edit_business_msg,
)
from gbe.models import (
    Business,
    UserMessage,
)


class TestBusinessCreate(TestCase):
    '''Tests for index view'''
    view_name = 'business-add'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.profile = ProfileFactory()
        ProfileFactory(user_object__username="admin_img")

    def submit_business(self, image=None):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)

        data = {'name': 'business for %s' % self.profile.display_name,
                'website': 'foo.bar.com/~quux',
                'description': 'stuff about business',
                'physical_address': "the place where you live",
                'publish_physical_address': True}
        if image:
            data['upload_img'] = image
        business_count = self.profile.business_set.all().count()
        response = self.client.post(
            url,
            data,
            follow=True)
        return response, business_count

    def test_register_business(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tell Us About Your Business")

    def test_register_business_w_image(self):
        pic_filename = open("tests/gbe/gbe_pagebanner.png", 'rb')
        response, business_count = self.submit_business(pic_filename)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "gbe_pagebanner.png")

    def test_register_business_friendly_urls(self):
        response, business_count = self.submit_business()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            1,
            self.profile.business_set.all().count()-business_count)

    def test_register_business_invalid_post(self):
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls')
        response = self.client.get(url)

        response = self.client.post(
            url,
            data={'website': 'foo.bar.com/~quux',
                  'description': 'stuff about business',
                  'physical_address': "the place where you live",
                  'publish_physical_address': True})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_create_business_make_message(self):
        response, business_count = self.submit_business()
        assert_alert_exists(
            response, 'success', 'Success', default_create_business_msg)


class TestBusinessEdit(TestCase):
    view_name = 'business-update'

    '''Tests for edit_persona view'''
    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.expected_string = 'Tell Us About Your Business'
        self.business = BusinessFactory()
        self.profile = self.business.owners.all().first()

    def submit_business(self, image=None, delete_image=False):
        login_as(self.profile, self)
        old_name = self.business.name
        new_name = "Fifi"
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.business.pk])
        data = {'name': new_name,
                'website': 'foo.bar.com/~quux',
                'description': 'stuff about business',
                'physical_address': "the place where you live",
                'publish_physical_address': True}
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

    def test_edit_business(self):
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.business.pk])
        login_as(self.profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.expected_string)
        self.assertNotContains(response, "Create Troupe")

    def test_edit_persona_load_img(self):
        set_image(self.business)

        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.business.pk])
        login_as(self.profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.business.img.url)

    def test_wrong_profile(self):
        viewer = ProfileFactory()
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.business.pk])
        login_as(viewer, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_persona_change_stage_name(self):
        response, new_name = self.submit_business()
        business_reloaded = Business.objects.get(pk=self.business.pk)
        self.assertEqual(business_reloaded.name, new_name)

    def test_edit_persona_change_image(self):
        ProfileFactory(user_object__username="admin_img")
        pic_filename = open("tests/gbe/gbe_pagebanner.png", 'rb')

        response, new_name = self.submit_business(pic_filename)
        business_reloaded = Business.objects.get(pk=self.business.pk)
        self.assertEqual(str(business_reloaded.img), "gbe_pagebanner.png")

    def test_change_image_foreign_char(self):
        ProfileFactory(user_object__username="admin_img")
        pic_filename = open("tests/gbe/gbe_pagebanner.png", 'rb')

        login_as(self.profile, self)
        new_name = "Bitsy Brûlée"
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.business.pk])
        data = {'name': new_name,
                'website': 'foo.bar.com/~quux',
                'description': 'stuff about business',
                'physical_address': "the place where you live",
                'publish_physical_address': True,
                'upload_img': pic_filename}

        response = self.client.post(
            url,
            data,
            follow=True
        )
        business_reloaded = Business.objects.get(pk=self.business.pk)
        self.assertEqual(str(business_reloaded.img), "gbe_pagebanner.png")

    def test_edit_business_remove_image(self):
        set_image(self.business)
        self.assertEqual(str(self.business.img), "gbe_pagebanner.png")
        response, new_name = self.submit_business(delete_image=True)
        business_reloaded = Business.objects.get(pk=self.business.pk)
        self.assertEqual(business_reloaded.img, None)

    def test_edit_business_invalid_post(self):
        login_as(self.profile, self)
        old_name = self.business.name
        new_name = "Fifi"
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      args=[self.business.pk])
        response = self.client.post(
            url,
            data={'name': new_name,
                  'website': 'foo.bar.com/~quux',
                  'physical_address': "the place where you live",
                  'publish_physical_address': True,}
        )
        self.assertContains(response, self.expected_string)
        business_reloaded = Business.objects.get(pk=self.business.pk)
        self.assertEqual(business_reloaded.name, old_name)

    def test_edit_business_make_message(self):
        response, new_name = self.submit_business()
        assert_alert_exists(
            response, 'success', 'Success', default_edit_business_msg)

    def test_edit_business_has_message(self):
        msg = UserMessageFactory(
            view='BusinessUpdate',
            code='SUCCESS')
        response, new_name = self.submit_business()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
