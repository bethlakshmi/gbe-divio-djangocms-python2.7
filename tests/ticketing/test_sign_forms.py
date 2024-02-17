from django.test import TestCase
from django.urls import reverse
from tests.contexts import ActTechInfoContext
from tests.factories.gbe_factories import (
    UserFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    login_as,
)
from tests.functions.ticketing_functions import set_form
from gbetext import (
    sign_form_msg,
    all_signed_msg,
)
from tests.factories.ticketing_factories import RoleEligibilityConditionFactory
from ticketing.models import Signature


class TestSignForms(TestCase):
    '''Tests for index view'''
    view_name = 'sign_forms'

    formset_data = {
        'form-0-id': '',
        'form-0-signed_file': 1,
        'form-0-name_signed': 'Test Name of Signer',
        'form-TOTAL_FORMS': 1,
        'form-INITIAL_FORMS': 0,
        'form-MIN_NUM_FORMS': 1,
        'form-MAX_NUM_FORMS': 1000,
    }

    @classmethod
    def setUpTestData(cls):
        cls.context = ActTechInfoContext()
        cls.url = reverse(cls.view_name, urlconf='ticketing.urls')
        # add conf and next
        cls.priv_url = "%s??conf_slug=%s&next=%s" % (
            reverse(cls.view_name,
                    urlconf='ticketing.urls',
                    args=[cls.context.performer.contact.user_object.pk]),
            cls.context.conference,
            reverse("manage_signatures", urlconf='ticketing.urls'))
        cls.condition = RoleEligibilityConditionFactory(
            role="Performer",
            checklistitem__description="Form to Sign!",
            checklistitem__e_sign_this=set_form())
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Registrar')

    def test_get_form(self):
        login_as(self.context.performer.contact, self)
        response = self.client.get(self.url)
        self.assertContains(response,
                            self.condition.checklistitem.description)
        self.assertContains(
            response,
            self.condition.checklistitem.e_sign_this.url)
        self.assertContains(response, sign_form_msg)

    def test_sign_forms(self):
        login_as(self.context.performer.contact, self)
        response = self.client.post(
            self.url,
            self.formset_data,
            follow=True)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        self.assertNotContains(response, "Sign some Forms!")
        self.assertEqual(Signature.objects.filter(
            user=self.context.performer.contact.user_object).count(), 1)
        assert_alert_exists(
            response,
            'success',
            'Success',
            all_signed_msg)

    def test_empty_forms(self):
        login_as(self.context.performer.contact, self)
        data = self.formset_data.copy()
        data['form-0-name_signed'] = ''
        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, sign_form_msg)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, "Please submit at least 1 form.")

    def test_all_forms_signed(self):
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, sign_form_msg)
        self.assertContains(response, "You have no forms to sign")

    def test_get_form_w_privilege(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.priv_url)
        self.assertContains(
            response,
            "Signer: %s, Conference: %s" % (
                self.context.performer.contact.display_name,
                self.context.conference.conference_slug))

    def test_sign_forms_w_privilege(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.priv_url,
            self.formset_data,
            follow=True)
        self.assertRedirects(response, "%s?conf_slug=%s" % (
            reverse("manage_signatures", urlconf='ticketing.urls'),
            self.context.conference.conference_slug))
        self.assertNotContains(response, "Sign some Forms!")
        self.assertEqual(Signature.objects.filter(
            user=self.context.performer.contact.user_object).count(), 1)
        assert_alert_exists(
            response,
            'success',
            'Success',
            "%s  Signatures complete for user %s, conference %s" % (
                all_signed_msg,
                str(self.context.performer.contact),
                self.context.conference.conference_name))
