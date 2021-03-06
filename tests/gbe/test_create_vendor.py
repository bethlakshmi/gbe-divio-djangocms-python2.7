from django.urls import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    BusinessFactory,
    ConferenceFactory,
    ProfileFactory,
    UserMessageFactory,
    VendorFactory
)
from tests.functions.ticketing_functions import setup_fees
from tests.functions.gbe_functions import (
    current_conference,
    login_as,
    assert_alert_exists,
    make_vendor_app_purchase,
    make_vendor_app_ticket
)
from gbetext import (
    default_vendor_submit_msg,
    default_vendor_draft_msg
)
from gbe.models import (
    Conference,
    UserMessage
)


class TestCreateVendor(TestCase):
    '''Tests for create_vendor view'''
    view_name = 'vendor_create'

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.profile = ProfileFactory()
        self.conference = current_conference()
        UserMessage.objects.all().delete()
        self.business = BusinessFactory(owners=[self.profile])

    def get_form(self, submit=False, invalid=False):
        form = {'thebiz-business': self.business.pk}
        if submit:
            form['submit'] = True
        if invalid:
            form['thebiz-business'] = self.business.pk + 10
        return form

    def post_paid_vendor_submission(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        username = self.profile.user_object.username
        make_vendor_app_purchase(self.conference, self.profile.user_object)
        login_as(self.profile, self)
        data = self.get_form(submit=True)
        response = self.client.post(url,
                                    data,
                                    follow=True)
        return response, data

    def post_unpaid_vendor_draft(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        data = self.get_form()
        data['draft'] = True
        response = self.client.post(url,
                                    data,
                                    follow=True)
        return response, data

    def test_create_vendor_post_form_valid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        event_id = make_vendor_app_ticket(self.conference)
        response, data = self.post_unpaid_vendor_draft()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to GBE')
        draft_string = (
            '<i class="fas fa-arrow-alt-circle-right"></i> <b>%s - %s</b>'
            ) % (self.business.name, self.conference.conference_slug)
        self.assertContains(response, "(Click to edit)")
        self.assertContains(response, draft_string)

    def test_create_vendor_post_form_valid_submit(self):
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.profile, self)
        tickets = setup_fees(self.conference, is_vendor=True)

        data = self.get_form(submit=True)
        data['main_ticket'] = tickets[0].pk
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fee has not been Paid')

    def test_create_vendor_post_form_invalid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        data = self.get_form(invalid=True)
        response = self.client.post(
            url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice.")

    def test_create_vendor_post_form_not_my_biz(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        data = self.get_form()
        other_biz = BusinessFactory()
        data['thebiz-business'] = other_biz.pk
        login_as(self.profile, self)
        response = self.client.post(
            url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice.")

    def test_create_vendor_with_get_request(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vendor Application')

    def test_create_vendor_with_no_business(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertContains(response, 'Tell Us About Your Business')

    def test_create_vendor_post_with_vendor_app_paid(self):
        response, data = self.post_paid_vendor_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to GBE")
        self.assertContains(response, "(Click to view)")
        self.assertContains(response, self.business.name)

    def test_create_paid_vendor_w_other_vendor_paid(self):
        VendorFactory(b_conference=self.conference, submitted=True)
        response, data = self.post_paid_vendor_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to GBE")
        self.assertContains(response, "(Click to view)")
        self.assertContains(response, self.business.name)

    def test_create_vendor_post_with_vendor_old_comp(self):
        comped_vendor = VendorFactory(
            submitted=True,
            business=self.business,
            b_conference=ConferenceFactory(status='completed')
        )
        response, data = self.post_paid_vendor_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to GBE")
        self.assertContains(response, "(Click to view)")
        self.assertContains(response, self.business.name)

    def test_create_vendor_post_with_second_vendor_app_paid(self):
        prev_vendor = VendorFactory(
            submitted=True,
            business=self.business,
            b_conference=self.conference
        )
        make_vendor_app_purchase(self.conference, self.profile.user_object)
        response, data = self.post_paid_vendor_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to GBE")
        self.assertContains(response, "(Click to view)")
        self.assertContains(response, self.business.name)

    def test_vendor_submit_make_message(self):
        response, data = self.post_paid_vendor_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_vendor_submit_msg)

    def test_vendor_draft_make_message(self):
        response, data = self.post_unpaid_vendor_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_vendor_draft_msg)

    def test_vendor_submit_has_message(self):
        msg = UserMessageFactory(
            view='MakeVendorView',
            code='SUBMIT_SUCCESS')
        response, data = self.post_paid_vendor_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_vendor_draft_has_message(self):
        msg = UserMessageFactory(
            view='MakeVendorView',
            code='DRAFT_SUCCESS')
        response, data = self.post_unpaid_vendor_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
