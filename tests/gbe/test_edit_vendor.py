from django.urls import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    BusinessFactory,
    ConferenceFactory,
    ProfileFactory,
    UserFactory,
    VendorFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    make_vendor_app_purchase,
    make_vendor_app_ticket,
)
from gbetext import (
    default_vendor_submit_msg,
    default_vendor_draft_msg,
    payment_details_error,
    payment_needed_msg,
)
from gbe.models import (
    UserMessage,
    Vendor,
)
from tests.functions.ticketing_functions import setup_fees


class TestEditVendor(TestCase):
    '''Tests for edit_vendor view'''
    view_name = "vendor_edit"

    # this test case should be unnecessary, since edit_vendor should go away
    # for now, test it.

    def setUp(self):
        UserMessage.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.profile = ProfileFactory()
        self.business = BusinessFactory(owners=[self.profile])

    def get_vendor_form(self, submit=False, invalid=False):
        form = {'thebiz-business': self.business.pk}
        if submit:
            form['submit'] = True
        if invalid:
            form['thebiz-business'] = self.business.pk + 10
        return form

    def post_edit_paid_vendor_submission(self):
        vendor = VendorFactory(business=self.business)
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        make_vendor_app_purchase(vendor.b_conference, self.profile.user_object)
        response = self.client.post(url, data, follow=True)
        return response

    def post_edit_paid_vendor_draft(self):
        vendor = VendorFactory(business=self.business)
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form()
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
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_vendor_edit_post_form_not_valid(self):
        vendor = VendorFactory(business=self.business)
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(invalid=True)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vendor Application')

    def test_vendor_edit_post_form_valid(self):
        response = self.post_edit_paid_vendor_draft()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to GBE")
        assert_alert_exists(
            response, 'success', 'Success', default_vendor_draft_msg)

    def test_vendor_edit_post_form_valid_submit_paid_wrong_conf(self):
        vendor = VendorFactory(business=self.business)
        tickets = setup_fees(vendor.b_conference, is_vendor=True)

        make_vendor_app_purchase(
            ConferenceFactory(
                status="completed"),
            self.profile.user_object)
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['main_ticket'] = tickets[0].pk
        data['add_ons'] = tickets[1].pk
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fee has not been Paid')
        self.assertContains(response, tickets[0].title)
        self.assertContains(response, tickets[1].title)

    def test_vendor_edit_post_form_valid_submit_bad_pay_choice(self):
        vendor = VendorFactory(business=self.business)
        tickets = setup_fees(vendor.b_conference, is_vendor=True)
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['main_ticket'] = tickets[0].pk + 1000
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, payment_details_error)
        self.assertContains(
            response,
            "Select a valid choice.")

    def test_vendor_edit_post_form_valid_submit_no_main_ticket(self):
        vendor = VendorFactory(business=self.business)

        tickets = setup_fees(vendor.b_conference, is_vendor=True)
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['add_ons'] = tickets[1].pk
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, payment_details_error)
        self.assertContains(response, "This field is required.")

    def test_edit_bid_get(self):
        '''edit_bid, not post, should take us to edit process'''
        msg = UserMessageFactory(
            view='MakeVendorView',
            code='FEE_MESSAGE',
            summary="Vendor Bid Instructions",
            description="Test Fee Instructions Message")
        vendor = VendorFactory(business=self.business)
        tickets = setup_fees(vendor.b_conference, is_vendor=True)
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<h2 class="gbe-title">Vendor Application</h2>',
            html=True)
        self.assertContains(response, "Test Fee Instructions Message")
        self.assertContains(response, tickets[0].title)
        self.assertContains(response, tickets[1].cost)

    def test_edit_paid_bid_get(self):
        '''edit_bid, not post, should take us to edit process'''
        vendor = VendorFactory(business=self.business)
        tickets = setup_fees(vendor.b_conference, is_vendor=True)
        make_vendor_app_purchase(vendor.b_conference,
                                 self.profile.user_object)
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<h2 class="gbe-title">Vendor Application</h2>',
            html=True)
        self.assertContains(response, 'value="Submit For Approval"')
        self.assertNotContains(response, tickets[0].title)
        self.assertNotContains(response, tickets[1].title)

    def test_edit_bid_get_no_help(self):
        '''edit_bid, not post, should take us to edit process'''
        vendor = VendorFactory(
            business=self.business,
            help_times="",
            help_description="")
        login_as(self.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<h2 class="gbe-title">Vendor Application</h2>',
            html=True)

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
