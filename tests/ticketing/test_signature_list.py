from django.test import TestCase
from django.urls import reverse
from tests.contexts import ActTechInfoContext
from tests.factories.gbe_factories import (
    UserFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import login_as
from tests.functions.ticketing_functions import set_form
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    SignatureFactory,
)


class TestSignatureList(TestCase):
    '''Tests for index view'''
    view_name = 'signature_list'

    @classmethod
    def setUpTestData(cls):
        cls.context = ActTechInfoContext()
        cls.url = reverse(cls.view_name, urlconf='ticketing.urls')
        # add conf and next
        cls.condition = RoleEligibilityConditionFactory(
            role="Performer",
            checklistitem__description="Form to Sign!",
            checklistitem__e_sign_this=set_form())
        cls.signature = SignatureFactory(
            user=cls.context.performer.contact.user_object,
            conference=cls.context.conference,
            signed_file=cls.condition.checklistitem.e_sign_this)
        cls.signature_other_user = SignatureFactory(
            conference=cls.context.conference,
            signed_file=cls.condition.checklistitem.e_sign_this)

    def test_get_signed(self):
        login_as(self.context.performer.contact, self)
        response = self.client.get(self.url)
        self.assertContains(response,
                            self.signature.signed_file)
        self.assertContains(response, self.signature.name_signed)
        self.assertContains(response, self.context.conference.conference_name)
        self.assertNotContains(response, self.signature_other_user.name_signed)

    def test_no_forms_signed(self):
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertNotContains(response,
                               self.signature.signed_file)
        self.assertNotContains(response, self.signature.name_signed)
        self.assertNotContains(response,
                               self.context.conference.conference_name)
