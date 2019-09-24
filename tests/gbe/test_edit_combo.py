import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client

from tests.factories.gbe_factories import (
    PersonaFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    location,
)


# class TestEditCombo(TestCase):
#     '''Tests for create_combo view'''
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.client = Client()
#         self.combo_string = 'a one-off group of performers working'

#     def test_edit_combo(self):
#         '''edit_troupe view, create flow
#         '''
#         contact = PersonaFactory()
#         request = self.factory.get('/combo/create/')
#         request.user = UserFactory()
#         response = create_combo(request)
#         self.assertEqual(response.status_code, 302)
#         user = UserFactory()
#         login_as(user, self)
#         request.user = user
#         request.session = {'cms_admin_site': 1}
#         response = create_combo(request)
#         nt.assert_equal(response.status_code, 302)
#         nt.assert_equal(location(response),
#                         '/update_profile?next=/combo/create')
#         request.user = contact.performer_profile.user_object
#         login_as(contact.performer_profile, self)
#         response = create_combo(request)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(self.combo_string in response.content)
