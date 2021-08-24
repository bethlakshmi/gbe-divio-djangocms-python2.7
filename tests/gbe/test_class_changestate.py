import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.contexts import ClassContext
from tests.factories.gbe_factories import (
    ClassFactory,
    ProfileFactory
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestClassChangestate(TestCase):
    '''Tests for act_changestate view'''
    view_name = 'class_changestate'

    def setUp(self):
        self.client = Client()
        self.klass = ClassFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Class Coordinator')
        self.data = {'accepted': '3'}

    def test_class_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        url = reverse(self.view_name,
                      args=[self.klass.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        nt.assert_equal(response.status_code, 302)

    def test_class_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        url = reverse(self.view_name,
                      args=[self.klass.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.post(url, data=self.data)
        nt.assert_equal(response.status_code, 403)

    def test_class_changestate_clear_schedule(self):
        '''The proper coordinator is changing the state, it works'''
        context = ClassContext()
        url = reverse(self.view_name,
                      args=[context.bid.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data={'accepted': '1'})
        assert not context.bid.scheduler_events.exists()

    def test_class_changestate_immediate_schedule(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        context = ClassContext()
        url = reverse(self.view_name,
                      args=[context.bid.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(
            url,
            data={'accepted': '3', 'extra_button': "Schedule >>"},
            follow=True)
        self.assertRedirects(
            response,
            "%s?accepted_class=%d" % (
                reverse("create_class_wizard",
                        urlconf='gbe.scheduling.urls',
                        args=[context.conference.conference_slug]),
                context.bid.eventitem_id))

    def test_class_changestate_bad_data(self):
        '''The proper coordinator is changing the state, it works'''
        url = reverse(self.view_name,
                      args=[self.klass.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data={'accepted': '-1'})
        assert response.status_code == 200
        self.assertContains(response, 'Bid Information')
