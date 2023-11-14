from django.urls import reverse
from django.test import TestCase
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.gbe_factories import (
    VendorFactory,
    ProfileFactory,
)
from tests.contexts import ClassContext
from gbe.models import Conference
from gbetext import eval_report_explain_msg
from tests.factories.scheduler_factories import (
    EventEvalGradeFactory,
    EventEvalBooleanFactory,
    EventEvalCommentFactory,
)


class TestVendorHistory(TestCase):
    view_name = "vendor_history"

    @classmethod
    def setUpTestData(cls):
        cls.priv_profile = ProfileFactory()
        cls.inactive = ProfileFactory(user_object__is_active=False)
        cls.vendor = VendorFactory()
        cls.vendor.business.owners.add(cls.inactive)
        cls.other_vendor = VendorFactory(b_conference__status="completed")
        cls.inactive_vendor = VendorFactory(business__owners=[cls.inactive])
        grant_privilege(cls.priv_profile, 'Vendor Coordinator')
        cls.url = reverse(cls.view_name, urlconf="gbe.reporting.urls")

    def test_not_visible_without_permission(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_success(self):
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.vendor.business.name)
        self.assertContains(response, self.other_vendor.business.name)
        self.assertContains(response, self.inactive_vendor.business.name)
        self.assertContains(response,
                            self.vendor.b_conference.conference_slug)
        self.assertContains(response,
                            self.other_vendor.b_conference.conference_slug)
        self.assertContains(response,
                            self.inactive_vendor.b_conference.conference_slug)
        self.assertContains(
            response,
            self.vendor.business.owners.filter(
                user_object__is_active=True).first().user_object.email)
        self.assertContains(
            response,
            self.other_vendor.business.owners.first().phone)
        self.assertNotContains(response, self.inactive)
        self.assertContains(response, "All owners are inactive")
