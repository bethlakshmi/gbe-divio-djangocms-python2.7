from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    StyleValueFactory,
    StyleValueImageFactory,
    StyleVersionFactory,
    UserFactory,
)
from filer.models.imagemodels import Image
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
    set_image
)
from easy_thumbnails.files import get_thumbnailer


class TestManageTheme(TestCase):
    view_name = "manage_theme"
    px_input = ('<input type="number" name="%d-value_%d" value="%d" ' +
                'class="pixel-input" required id="id_%d-value_%d">')

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory().user_object
        grant_privilege(self.user, u'Theme Editor')

        self.value = StyleValueFactory()
        self.url = reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk])
        self.title = "Manage {}, version {:.1f}".format(
            self.value.style_version.name,
            self.value.style_version.number)
        self.style_url = reverse(
            "theme_style",
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk])

    def test_no_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response,
                             "/login/?next=%s" % self.url,
                             fetch_redirect_response=False)

    def test_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_get(self):
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, reverse(
            "clone_theme",
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk]))
        self.assertContains(response, self.title)
        self.assertContains(response, self.value.value)
        self.assertContains(response,
                            self.value.style_property.selector)
        self.assertContains(response,
                            self.value.style_property.selector.used_for)
        self.assertContains(response,
                            self.value.style_property.style_property)
        self.assertContains(response, self.style_url)

    def test_get_image(self):
        Image.objects.all().delete()
        other_image = set_image()
        image_style = StyleValueImageFactory(
            style_version=self.value.style_version,
            image=set_image(folder_name='Backgrounds'))

        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response,
                            image_style.style_property.selector)
        self.assertContains(response,
                            image_style.style_property.style_property)
        self.assertContains(
            response,
            '''<input type="radio" name="%s-image" value="%s"
            id="id_%s-image_1" checked>''' % (
                image_style.pk,
                image_style.image.pk,
                image_style.pk),
            html=True)
        self.assertNotContains(
            response,
            get_thumbnailer(other_image).get_thumbnail(
                {'size': (100, 100), 'crop': False}).url)

    def test_get_empty(self):
        empty = StyleVersionFactory()
        login_as(self.user, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[empty.pk]))
        self.assertContains(
            response,
            "Manage {}, version {:.1f}".format(empty.name, empty.number))
        self.assertContains(response, reverse(
            "theme_style",
            urlconf="gbe.themes.urls",
            args=[empty.pk]))

    def test_get_bad_id(self):
        login_as(self.user, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk+1]))
        self.assertEqual(404, response.status_code)

    def test_post_finish(self):
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            '%s-value_0' % self.value.pk: "rgba(255,255,255,0)",
            '%s-style_property' % self.value.pk: self.value.style_property.pk,
            'finish': "Finish",
            }, follow=True)
        self.assertContains(
            response,
            "Updated %s" % self.value.style_version)
        self.assertRedirects(response, "%s?changed_id=%d" % (
            reverse('themes_list', urlconf='gbe.themes.urls'),
            self.value.style_version.pk))

    def test_post_update(self):
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            '%s-value_0' % self.value.pk: "rgba(255,255,255,0)",
            '%s-style_property' % self.value.pk: self.value.style_property.pk,
            'update': "Update",
            }, follow=True)
        self.assertContains(response, self.title)
        self.assertContains(
            response,
            "Updated %s" % self.value.style_version)
        self.assertContains(response, 'rgba(255,255,255,0)')
        self.assertContains(response,
                            self.value.style_property.selector)
        self.assertContains(response,
                            self.value.style_property.selector.used_for)
        self.assertContains(response,
                            self.value.style_property.style_property)
        self.assertContains(response, self.style_url)

    def test_post_update_change_image(self):
        Image.objects.all().delete()
        other_image = set_image(folder_name='Backgrounds')
        image_style = StyleValueImageFactory(
            style_version=self.value.style_version,
            image=set_image(folder_name='Backgrounds'))
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            '%s-value_0' % self.value.pk: "rgba(255,255,255,0)",
            '%s-style_property' % self.value.pk: self.value.style_property.pk,
            '%s-style_property' % image_style.pk:
                image_style.style_property.pk,
            "%s-image" % image_style.pk: other_image.pk,
            "%s-add_image" % image_style.pk: "",
            'update': "Update",
            }, follow=True)
        self.assertContains(response,
                            image_style.style_property.selector)
        self.assertContains(response,
                            image_style.style_property.style_property)
        self.assertContains(
            response,
            '''<input type="radio" name="%s-image" value="%s"
            id="id_%s-image_2" checked>''' % (
                image_style.pk,
                other_image.pk,
                image_style.pk),
            html=True)

    def test_post_update_upload_image(self):
        Image.objects.all().delete()
        UserFactory(username='admin_img')
        image_style = StyleValueImageFactory(
            style_version=self.value.style_version,
            image=set_image(folder_name='Backgrounds'))
        file1 = open("tests/gbe/gbe_pagebanner.png", 'rb')
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            '%s-value_0' % self.value.pk: "rgba(255,255,255,0)",
            '%s-style_property' % self.value.pk: self.value.style_property.pk,
            '%s-style_property' % image_style.pk:
                image_style.style_property.pk,
            "%s-image" % image_style.pk: image_style.image.pk,
            "%s-add_image" % image_style.pk: file1,
            'update': "Update",
            }, follow=True)
        self.assertContains(response,
                            image_style.style_property.selector)
        self.assertContains(response,
                            image_style.style_property.style_property)
        self.assertContains(
            response,
            '''<input type="radio" name="%s-image" value="%s"
            id="id_%s-image_1" checked>''' % (
                image_style.pk,
                image_style.image.pk + 1,
                image_style.pk),
            html=True)

    def test_cancel(self):
        login_as(self.user, self)
        response = self.client.post(
            self.url,
            data={'cancel': "Cancel"},
            follow=True)
        self.assertContains(response, "The last update was canceled.")
        self.assertRedirects(response,
                             reverse("themes_list", urlconf="gbe.themes.urls"))

    def test_post_bad_data(self):
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            'finish': "Finish",
            }, follow=True)
        self.assertContains(response, self.title)
        self.assertContains(
            response,
            "Something was wrong, correct the errors below and try again.")
        self.assertContains(response, "This field is required.")
        self.assertContains(response, self.style_url)

    def test_get_complicated_property(self):
        from gbe_forms_text import style_value_help
        complex_value = StyleValueFactory(
            value="5px 4px 3px rgba(10,10,10,1)",
            parseable_values="5 4 3 rgba(10,10,10,1)",
            style_property__style_property="text-shadow",
            style_property__value_type="px px px rgba",
            style_property__value_template="{}px {}px {}px {}",
            style_property__selector=self.value.style_property.selector,
            style_version=self.value.style_version)
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            self.px_input % (complex_value.pk, 0, 5, complex_value.pk, 0),
            html=True)
        self.assertContains(
            response,
            self.px_input % (complex_value.pk, 1, 4, complex_value.pk, 1),
            html=True)
        self.assertContains(
            response,
            self.px_input % (complex_value.pk, 2, 3, complex_value.pk, 2),
            html=True)
        self.assertContains(response,
                            complex_value.style_property.selector)
        self.assertContains(response,
                            complex_value.style_property.style_property)
        self.assertContains(response, reverse(
            "clone_theme",
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk]))
        self.assertContains(response, style_value_help["text-shadow-0"])
        self.assertContains(response, style_value_help["text-shadow-1"])
        self.assertContains(response, style_value_help["text-shadow-2"])
        self.assertContains(response, style_value_help["text-shadow-3"])

    def test_get_complicated_messed_up_property(self):
        from gbe_forms_text import theme_help
        complex_value = StyleValueFactory(
            value="5px 4px rgba(10,10,10,1)",
            parseable_values="5px 4px rgba(10,10,10,1)",
            style_property__value_type="px px px rgba",
            style_property__selector=self.value.style_property.selector,
            style_version=self.value.style_version)
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, "%s, VALUES: %s" % (
            theme_help['mismatch'],
            "[\'5px\', \'4px\', \'rgba(10,10,10,1)\']"))

    def test_post_complicated_property(self):
        complex_value = StyleValueFactory(
            value="5px 4px 3px rgba(10,10,10,1)",
            parseable_values="5 4 3 rgba(10,10,10,1)",
            style_property__value_type="px px px rgba",
            style_property__value_template="{}px {}px {}px {}",
            style_property__selector=self.value.style_property.selector,
            style_version=self.value.style_version)
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            '%s-value_0' % self.value.pk: "rgba(255,255,255,0)",
            '%s-style_property' % self.value.pk: self.value.style_property.pk,
            '%s-value_0' % complex_value.pk: "0",
            '%s-style_property' % (
                complex_value.pk): complex_value.style_property.pk,
            '%s-value_1' % complex_value.pk: "10",
            '%s-value_2' % complex_value.pk: "15",
            '%s-value_3' % complex_value.pk: "rgba(50,50,50,0.5)",
            'update': "Update",
            }, follow=True)
        self.assertContains(
            response,
            self.px_input % (complex_value.pk, 0, 0, complex_value.pk, 0),
            html=True)
        self.assertContains(
            response,
            self.px_input % (complex_value.pk, 1, 10, complex_value.pk, 1),
            html=True)
        self.assertContains(
            response,
            self.px_input % (complex_value.pk, 2, 15, complex_value.pk, 2),
            html=True)
        self.assertContains(response, "rgba(50,50,50,0.5)")
        self.assertContains(response,
                            complex_value.style_property.selector)
        self.assertContains(response,
                            complex_value.style_property.style_property)
        self.assertContains(response, reverse(
            "clone_theme",
            urlconf="gbe.themes.urls",
            args=[self.value.style_version.pk]))

    def test_post_complicated_messed_up_property(self):
        from gbe_forms_text import theme_help
        complex_value = StyleValueFactory(
            value="5px 4px 3px",
            parseable_values="5 4 3",
            style_property__value_type="px px px rgba",
            style_property__value_template="{}px {}px {}px {}",
            style_property__selector=self.value.style_property.selector,
            style_version=self.value.style_version)
        login_as(self.user, self)
        response = self.client.post(self.url, data={
            '%s-value_0' % self.value.pk: "rgba(255,255,255,0)",
            '%s-style_property' % self.value.pk: self.value.style_property.pk,
            '%s-value_0' % complex_value.pk: "0",
            '%s-style_property' % (
                complex_value.pk): complex_value.style_property.pk,
            '%s-value_1' % complex_value.pk: "10",
            '%s-value_2' % complex_value.pk: "15",
            '%s-value_3' % complex_value.pk: "rgba(50,50,50,0.5)",
            'update': "Update",
            }, follow=True)
        self.assertContains(response, "%s, VALUES: %s" % (
            theme_help['mismatch'],
            "[\'5\', \'4\', \'3\']"))
        self.assertContains(
            response,
            "Something was wrong, correct the errors below and try again.")

    def test_get_bad_value_template(self):
        from gbe_forms_text import theme_help
        complex_value = StyleValueFactory(
            value="5px 4px 3px rgba(10,10,10,1) bad",
            parseable_values="5 4 3 rgba(10,10,10,1) bad",
            style_property__style_property="text-shadow",
            style_property__value_type="px px px rgba bad",
            style_property__value_template="{}px {}px {}px {} bad",
            style_property__selector=self.value.style_property.selector,
            style_version=self.value.style_version)
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, "%s, VALUES: %s" % (
            theme_help['bad_elem'],
            "px px px rgba bad"))
