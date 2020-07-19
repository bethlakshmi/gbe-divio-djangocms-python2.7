import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.urls import reverse


class TestHandleUserContactEmailView(TestCase):
    view_name = 'handle_user_contact_email'

    def setUp(self):
        self.client = Client()

    def get_form(self, invalid=False):
        form = {'name': "Bob",
                'email': "bob@bob.com",
                'subject': 'Test Subject',
                'message': 'Bob says hello'}
        if invalid:
            del(form['email'])
        return form

    def test_user_contact_email_valid_form(self):
        url = reverse(self.view_name, urlconf='gbe.urls')
        data = self.get_form()
        with self.settings(USER_CONTACT_RECIPIENT_ADDRESSES=['a@b.com']):
            response = self.client.post(url, data=data, follow=True)
            nt.assert_equal(200, response.status_code)

    def test_user_contact_email_invalid_form(self):
        url = reverse(self.view_name, urlconf='gbe.urls')
        data = self.get_form(invalid=True)
        response = self.client.post(url, data=data, follow=True)
        nt.assert_equal(200, response.status_code)
