import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
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

    def test_class_accepted_displays_on_scheduler(self):
        '''check that bid acceptance sets e_title & e_description'''
        self.klass.e_title = ''
        self.klass.e_description = ''
        self.klass.save()
        url = reverse(self.view_name,
                      args=[self.klass.pk],
                      urlconf='gbe.urls')
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        sched_url = reverse('create_class_wizard',
                            urlconf='gbe.scheduling.urls',
                            args=[self.klass.b_conference.conference_slug])
        response = self.client.post(sched_url)
        print response
        assert self.klass.b_title in response.content

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

    def test_class_changestate_bad_data(self):
        '''The proper coordinator is changing the state, it works'''
        url = reverse(self.view_name,
                      args=[self.klass.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data={'accepted': '-1'})
        assert response.status_code == 200
        assert 'Bid Information' in response.content
