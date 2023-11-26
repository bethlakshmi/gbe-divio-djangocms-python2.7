from django.test import (
    Client,
    TestCase
)
from django.contrib.auth.models import User
from tests.factories.gbe_factories import(
    ActFactory,
    BusinessFactory,
    ProfileFactory,
    StyleElementFactory,
    StyleGroupFactory,
    StyleLabelFactory,
    StylePropertyFactory,
    TestURLFactory,
    TechInfoFactory,
    UserMessageFactory,
    VendorFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    setup_admin_w_privs,
)
from django.contrib.admin.sites import AdminSite
from django.urls import reverse


class GBEAdminChangeListTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = setup_admin_w_privs([])

    def setUp(self):
        self.client = Client()
        login_as(self.privileged_user, self)

    def test_get_usermessage_item(self):
        msg = UserMessageFactory()
        response = self.client.get('/admin/gbe/usermessage/%d/change/' % (
            msg.pk), follow=True)
        self.assertContains(response, str(msg))

    def test_get_techinfo(self):
        act = ActFactory()
        response = self.client.get('/admin/gbe/techinfo/', follow=True)
        self.assertContains(response, "Techinfo: %s" % act.b_title)

    def test_get_techinfo_no_act(self):
        tech = TechInfoFactory()
        response = self.client.get('/admin/gbe/techinfo/', follow=True)
        self.assertContains(response, "Techinfo: (deleted act)")

    def test_get_vendor(self):
        inactive = ProfileFactory(user_object__is_active=False)
        vendor = VendorFactory(business__owners=[inactive])
        response = self.client.get('/admin/gbe/vendor/', follow=True)
        self.assertContains(response, str(inactive))
        self.assertContains(response, vendor.business.name)

    def test_get_business(self):
        inactive = ProfileFactory(user_object__is_active=False)
        business = BusinessFactory(owners=[inactive])
        response = self.client.get('/admin/gbe/business/', follow=True)
        self.assertContains(response, str(inactive))

    def test_get_styleproperty(self):
        style_property = StylePropertyFactory(
            label=StyleLabelFactory(),
            element=StyleElementFactory())
        response = self.client.get('/admin/gbe/styleproperty/', follow=True)
        self.assertContains(response, str(style_property.label))
        self.assertContains(response, str(style_property.element))

    def test_get_stylegroupedit(self):
        style_group = StyleGroupFactory()
        test_url = TestURLFactory()
        response = self.client.get(
            reverse("admin:gbe_stylegroup_change",
                    args=(style_group.id,)),
            follow=True)
        self.assertContains(response, str(test_url))
