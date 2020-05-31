from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
    UserFactory,
    VendorFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    location,
    make_vendor_app_purchase,
    make_vendor_app_ticket,
    set_image,
)
from gbetext import (
    default_vendor_submit_msg,
    default_vendor_draft_msg,
    payment_needed_msg,
)
from gbe.models import (
    UserMessage,
    Vendor,
)
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    PayPalSettingsFactory,
    TicketItemFactory,
)


class TestEditVendor(TestCase):
    '''Tests for edit_vendor view'''
    view_name = "vendor_edit"

    # this test case should be unnecessary, since edit_vendor should go away
    # for now, test it.

    def setUp(self):
        UserMessage.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.user = ProfileFactory().user_object

    def get_vendor_form(self, submit=False, invalid=False):
        form = {'thebiz-profile': 1,
                'thebiz-b_title': 'title here',
                'thebiz-b_description': 'description here',
                'thebiz-physical_address': '123 Maple St.',
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['thebiz-b_description'])
        return form

    def post_edit_paid_vendor_submission(self):
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['thebiz-profile'] = vendor.profile.pk
        make_vendor_app_purchase(vendor.b_conference,
                                 vendor.profile.user_object)
        response = self.client.post(url, data, follow=True)
        return response

    def post_edit_paid_vendor_draft(self):
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form()
        data['thebiz-profile'] = vendor.profile.pk
        data['draft'] = True
        response = self.client.post(url, data, follow=True)
        return response

    def test_edit_vendor_no_vendor(self):
        '''Should get 404 if no valid vendor ID'''
        url = reverse(self.view_name,
                      args=[0],
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_edit_vendor_no_profile(self):
        vendor = VendorFactory()
        login_as(UserFactory(), self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(
            response,
            reverse('profile_update',
                    urlconf='gbe.urls') + '?next=/vendor/create')

    def test_edit_vendor_wrong_user(self):
        vendor = VendorFactory()
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_vendor_edit_post_form_not_valid(self):
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(invalid=True)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vendor Application')

    def test_vendor_edit_post_form_valid(self):
        response = self.post_edit_paid_vendor_draft()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profile View")
        assert_alert_exists(
            response, 'success', 'Success', default_vendor_draft_msg)

    def test_vendor_edit_post_form_valid_submit_paid_wrong_conf(self):
        PayPalSettingsFactory()
        vendor = VendorFactory()
        event = BrownPaperEventsFactory(conference=vendor.b_conference,
                                        vendor_submission_event=True)
        ticket = TicketItemFactory(live=True, bpt_event=event)
        make_vendor_app_purchase(
            ConferenceFactory(
                status="completed"),
            vendor.profile.user_object)
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['thebiz-profile'] = vendor.profile.pk
        data['main_ticket'] = ticket.pk
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fee has not been Paid')
        self.assertContains(response, ticket.title)

    def test_edit_bid_get(self):
        '''edit_bid, not post, should take us to edit process'''
        msg = UserMessageFactory(
            view='MakeVendorView',
            code='FEE_MESSAGE',
            summary="Vendor Bid Instructions",
            description="Test Fee Instructions Message")
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<h2 class="subtitle">Vendor Application</h2>')
        self.assertContains(response, "Test Fee Instructions Message")

    def test_edit_paid_bid_get(self):
        '''edit_bid, not post, should take us to edit process'''
        vendor = VendorFactory()
        make_vendor_app_purchase(vendor.b_conference,
                                 vendor.profile.user_object)
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<h2 class="subtitle">Vendor Application</h2>')
        self.assertContains(response, 'value="Submit For Approval"')

    def test_edit_bid_get_no_help(self):
        '''edit_bid, not post, should take us to edit process'''
        vendor = VendorFactory(
            help_times="",
            help_description="")
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<h2 class="subtitle">Vendor Application</h2>')

    def test_vendor_submit_make_message(self):
        response = self.post_edit_paid_vendor_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_vendor_submit_msg)

    def test_vendor_submit_has_message(self):
        msg = UserMessageFactory(
            view='MakeVendorView',
            code='SUBMIT_SUCCESS')
        response = self.post_edit_paid_vendor_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_vendor_draft_has_message(self):
        msg = UserMessageFactory(
            view='MakeVendorView',
            code='DRAFT_SUCCESS')
        response = self.post_edit_paid_vendor_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_edit_vendor_load_img(self):
        vendor = VendorFactory()
        set_image(vendor)
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, vendor.img.url)

    def test_edit_change_image(self):
        ProfileFactory(user_object__username="admin_img")
        pic_filename = open("tests/gbe/gbe_pagebanner.png", 'rb')
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['thebiz-profile'] = vendor.profile.pk
        data['thebiz-upload_img'] = pic_filename
        make_vendor_app_purchase(vendor.b_conference,
                                 vendor.profile.user_object)
        response = self.client.post(url, data, follow=True)
        vendor_reloaded = Vendor.objects.get(pk=vendor.pk)
        self.assertEqual(str(vendor_reloaded.img), "gbe_pagebanner.png")

    def test_edit_remove_image(self):
        vendor = VendorFactory()
        set_image(vendor)
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['thebiz-profile'] = vendor.profile.pk
        data['thebiz-upload_img-clear'] = True
        make_vendor_app_purchase(vendor.b_conference,
                                 vendor.profile.user_object)
        response = self.client.post(url, data, follow=True)
        vendor_reloaded = Vendor.objects.get(pk=vendor.pk)
        self.assertEqual(vendor_reloaded.img, None)
