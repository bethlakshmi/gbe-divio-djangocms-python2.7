import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ClassProposalFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from django.core.exceptions import PermissionDenied


class TestReviewProposalList(TestCase):
    '''Tests for review_proposal_list view'''
    view_name = 'proposal_review_list'

    def setUp(self):
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Class Coordinator')

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_review_proposal_list_authorized_user(self):
        proposal = ClassProposalFactory()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)

    def test_review_proposal_list_bad_user(self):
        proposal = ClassProposalFactory()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)

    def test_review_proposal_list_no_user(self):
        proposal = ClassProposalFactory()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)
