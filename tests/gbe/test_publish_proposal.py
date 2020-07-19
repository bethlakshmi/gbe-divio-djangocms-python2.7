import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ClassProposalFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestPublishProposal(TestCase):
    '''Tests for publish_proposal view'''
    view_name = 'proposal_publish'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Class Coordinator')

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_publish_proposal_not_post(self):
        proposal = ClassProposalFactory()
        url = reverse(self.view_name, urlconf='gbe.urls', args=[proposal.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)

    def test_publish_proposal_post_no_form(self):
        proposal = ClassProposalFactory()
        url = reverse(self.view_name, urlconf='gbe.urls', args=[proposal.pk])
        login_as(self.privileged_user, self)
        response = self.client.post(url)
        nt.assert_equal(response.status_code, 200)

    def test_publish_proposal_post_valid_form(self):
        proposal = ClassProposalFactory()
        url = reverse(self.view_name, urlconf='gbe.urls', args=[proposal.pk])
        login_as(self.privileged_user, self)
        data = self.get_class_form()
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 200)
