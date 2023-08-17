from django.test import TestCase
from django.urls import reverse
from tests.factories.gbe_factories import (
    ActFactory,
    BioFactory,
    ClassFactory,
    CostumeFactory,
    ProfileFactory,
    VendorFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbetext import warn_user_merge_delete_2
from gbe.models import Profile


class TestMergeProfileExtra(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'merge_bios'
    counter = 0

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Registrar')

    def setUp(self):
        self.profile = ProfileFactory()
        self.avail_profile = ProfileFactory()
        self.url = reverse(self.view_name,
                          urlconf='gbe.urls',
                          args=[self.profile.pk, self.avail_profile.pk])

    def test_no_privilege(self):
        random_user = ProfileFactory().user_object
        login_as(random_user, self)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_error_on_self(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.urls',
                    args=[self.profile.pk, self.privileged_user.profile.pk]),
            follow=True)
        self.assertContains(response, warn_user_merge_delete_2)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_get_form_w_bios(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        target_bio = BioFactory(contact=self.profile)
        avail_bio = BioFactory(contact=self.avail_profile)
        act = ActFactory(bio__contact=self.profile)
        klass = ClassFactory(teacher_bio__contact=self.avail_profile)
        costume = CostumeFactory(profile=self.profile,
                                 bio=act.bio)
        response = self.client.get(self.url)
        self.assertContains(response, 'Merge Users - Merge Bios')
        self.assertContains(response, avail_bio.name)
        self.assertContains(response, "%s - %s: %s" % (
            act.b_conference.conference_slug,
            act.__class__.__name__,
            act.b_title))
        self.assertContains(response, "%s - %s: %s" % (
            klass.b_conference.conference_slug,
            klass.__class__.__name__,
            klass.b_title))
        self.assertContains(response, "%s - %s: %s" % (
            costume.b_conference.conference_slug,
            costume.__class__.__name__,
            costume.b_title))
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (target_bio.pk,
                                                target_bio.name),
            html=True)

    def test_get_form_w_business(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        vendor = VendorFactory()
        avail_vendor = VendorFactory()
        vendor.business.owners.add(self.profile)
        avail_vendor.business.owners.add(self.avail_profile)
        response = self.client.get(self.url)
        self.assertContains(response, 'Merge Users - Merge Bios')
        self.assertContains(response, avail_vendor.business.name)
        self.assertContains(response, "%s - %s: %s" % (
            vendor.b_conference.conference_slug,
            vendor.__class__.__name__,
            str(vendor)))
        self.assertContains(response, "%s - %s: %s" % (
            avail_vendor.b_conference.conference_slug,
            avail_vendor.__class__.__name__,
            str(avail_vendor)))
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (vendor.business.pk,
                                                vendor.business.name),
            html=True)
