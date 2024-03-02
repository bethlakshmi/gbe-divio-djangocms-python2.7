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
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    SignatureFactory,
)
from ticketing.models import Signature


class TestManageSignature(TestCase):
    '''Tests for index view'''
    view_name = 'manage_signatures'

    @classmethod
    def setUpTestData(cls):
        cls.context = ActTechInfoContext()
        cls.url = reverse(cls.view_name, urlconf='ticketing.urls')
        # add conf and next
        cls.condition = RoleEligibilityConditionFactory(
            role="Performer",
            checklistitem__description="Form to Sign!",
            checklistitem__e_sign_this=set_form())
        cls.condition2 = RoleEligibilityConditionFactory(
            role="Performer",
            checklistitem__description="Other Form to Sign!",
            checklistitem__e_sign_this=set_form())
        cls.signature = SignatureFactory(
            user=cls.context.performer.contact.user_object,
            conference=cls.context.conference,
            signed_file=cls.condition.checklistitem.e_sign_this)
        cls.signature2 = SignatureFactory(
            user=cls.context.performer.contact.user_object,
            conference=cls.context.conference,
            signed_file=cls.condition2.checklistitem.e_sign_this)
        cls.signature_other_user = SignatureFactory(
            conference=cls.context.conference,
            signed_file=cls.condition.checklistitem.e_sign_this)
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Registrar')

    def test_current_conf(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.context.conference.conference_name)
        self.assertContains(response,
                            self.signature.signed_file)
        self.assertContains(response, self.signature.name_signed)
        self.assertContains(response, self.signature2.name_signed)
        self.assertContains(response, self.signature_other_user.name_signed)
        self.assertContains(response,
                            self.context.performer.contact.display_name)
        self.assertContains(response, self.condition.checklistitem.e_sign_this)
        self.assertContains(response,
                            self.condition2.checklistitem.e_sign_this)
        self.assertNotContains(response, "SIGN HERE")

    def test_choose_conf_unsigned_user(self):
        context_unsigned = ActTechInfoContext()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url + "?conf_slug=" + (
            context_unsigned.conference.conference_slug))
        self.assertContains(response,
                            context_unsigned.conference.conference_slug)
        self.assertContains(response,
                            context_unsigned.performer.contact.display_name)
        self.assertContains(response, self.condition.checklistitem.description)
        self.assertContains(response,
                            self.condition2.checklistitem.description)
        self.assertContains(response, "SIGN HERE")

    def test_choose_conf_partially_signed_user(self):
        context_unsigned = ActTechInfoContext()
        signature = SignatureFactory(
            user=context_unsigned.performer.contact.user_object,
            conference=context_unsigned.conference,
            signed_file=self.condition.checklistitem.e_sign_this)
        login_as(self.privileged_user, self)
        response = self.client.get(self.url + "?conf_slug=" + (
            context_unsigned.conference.conference_slug))
        self.assertContains(response,
                            context_unsigned.conference.conference_slug)
        self.assertContains(response,
                            context_unsigned.performer.contact.display_name)
        self.assertContains(response, self.condition.checklistitem.e_sign_this)
        self.assertContains(response,
                            self.condition2.checklistitem.description)
        self.assertContains(response, "SIGN HERE")
