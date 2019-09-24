from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    current_conference,
    grant_privilege,
    login_as,
)
from gbetext import default_propose_submit_msg
from gbe.models import UserMessage


class TestProposeClass(TestCase):
    '''Tests for propose_class view'''
    view_name = 'class_propose'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')

    def get_class_form(self, valid=True):
        data = {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description',
                'type': 'Class',
                }
        if not valid:
            del(data['type'])
        return data

    def post_class_proposal(self):
        current_conference()
        url = reverse(self.view_name, urlconf="gbe.urls")
        data = self.get_class_form(valid=True)
        login_as(UserFactory(), self)
        response = self.client.post(url, data=data, follow=True)
        return response

    def test_propose_invalid_class(self):
        current_conference()
        url = reverse(self.view_name, urlconf="gbe.urls")
        data = self.get_class_form(valid=False)
        login_as(UserFactory(), self)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_propose_valid_class(self):
        response = self.post_class_proposal()
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Profile View" in response.content)

    def test_propose_class_get(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("I've Got An Idea!" in response.content)

    def test_propose_submit_make_message(self):
        response = self.post_class_proposal()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_propose_submit_msg)

    def test_propose_submit_has_message(self):
        msg = UserMessageFactory(
            view='ProposeClassView',
            code='SUBMIT_SUCCESS')
        response = self.post_class_proposal()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
