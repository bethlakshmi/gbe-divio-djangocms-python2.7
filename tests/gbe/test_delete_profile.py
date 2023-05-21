from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    BidEvaluationFactory,
    BioFactory,
    CostumeFactory,
    ProfileFactory,
    VendorFactory,
    VolunteerFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe.models import Profile
from tests.contexts.class_context import ClassContext
from tests.factories.ticketing_factories import PurchaserFactory


class TestAdminProfile(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'delete_profile'

    def setUp(self):
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')
        self.deleted_profile = ProfileFactory()

    def assert_deactivated(self, response, profile):
        self.assertRedirects(response, reverse('manage_users',
                                               urlconf='gbe.urls'))
        self.assertNotIn(profile.display_name, response)
        profile.user_object.refresh_from_db()
        self.assertFalse(profile.user_object.is_active)

    def test_admin_profile_no_such_profile(self):
        no_such_id = Profile.objects.latest('pk').pk + 1
        url = reverse(self.view_name,
                      args=[no_such_id],
                      urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_unauthorized_user(self):
        url = reverse(self.view_name,
                      args=[self.deleted_profile.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_delete_user(self):
        url = reverse(self.view_name,
                      args=[self.deleted_profile.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('manage_users',
                                               urlconf='gbe.urls'))
        self.assertNotIn(self.deleted_profile.display_name, response)
        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(pk=self.deleted_profile)

    def test_deactivate_if_booked(self):
        context = ClassContext()
        teacher_prof = context.teacher.contact
        url = reverse(self.view_name,
                      args=[teacher_prof.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assert_deactivated(response, teacher_prof)

    def test_deactivate_if_persona(self):
        persona_bearer = BioFactory()
        url = reverse(self.view_name,
                      args=[persona_bearer.contact.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assert_deactivated(response, persona_bearer.contact)

    def test_deactivate_if_volunteer(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.profile.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assert_deactivated(response, volunteer.profile)

    def test_deactivate_if_costume(self):
        costumer = CostumeFactory()
        url = reverse(self.view_name,
                      args=[costumer.profile.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assert_deactivated(response, costumer.profile)

    def test_deactivate_if_vendor(self):
        vendor = VendorFactory()
        profile = vendor.business.owners.all().first()
        url = reverse(self.view_name,
                      args=[profile.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assert_deactivated(response, profile)

    def test_deactivate_if_bideval(self):
        bid_eval = BidEvaluationFactory()
        url = reverse(self.view_name,
                      args=[bid_eval.evaluator.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assert_deactivated(response, bid_eval.evaluator)

    def test_deactivate_if_actbideval(self):
        bid_eval = BidEvaluationFactory()
        url = reverse(self.view_name,
                      args=[bid_eval.evaluator.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assert_deactivated(response, bid_eval.evaluator)

    def test_deactivate_if_purchaser(self):
        purchaser = PurchaserFactory(
            matched_to_user=self.deleted_profile.user_object)
        url = reverse(self.view_name,
                      args=[self.deleted_profile.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assert_deactivated(response, self.deleted_profile)
