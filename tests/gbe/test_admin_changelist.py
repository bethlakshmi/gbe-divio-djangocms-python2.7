from django.test import (
    Client,
    TestCase
)
from django.contrib.auth.models import User
from gbe.models import Event
from tests.factories.gbe_factories import(
    ActFactory,
    BusinessFactory,
    EventFactory,
    GenericEventFactory,
    ProfileFactory,
    StyleElementFactory,
    StyleGroupFactory,
    StyleLabelFactory,
    StylePropertyFactory,
    TestURLFactory,
    TechInfoFactory,
    VendorFactory,
)
from django.contrib.admin.sites import AdminSite
from django.urls import reverse


class GBEAdminChangeListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = 'mypassword'
        cls.privileged_user = User.objects.create_superuser(
            'myuser', 'myemail@test.com', cls.password)
        cls.privileged_user.pageuser.created_by_id = cls.privileged_user.pk
        cls.privileged_user.pageuser.save()

    def setUp(self):
        self.client = Client()
        self.client.login(
            username=self.privileged_user.username,
            password=self.password)

    def test_get_event_subclass(self):
        obj = GenericEventFactory()
        response = self.client.get('/admin/gbe/event/', follow=True)
        self.assertContains(response, "GenericEvent")

    def test_get_event_no_subclass(self):
        obj = EventFactory()
        response = self.client.get('/admin/gbe/event/', follow=True)
        self.assertContains(response, "Event")
        self.assertContains(response, str(obj))

    def test_get_techinfo(self):
        act = ActFactory()
        response = self.client.get('/admin/gbe/techinfo/', follow=True)
        print(response.content)
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
