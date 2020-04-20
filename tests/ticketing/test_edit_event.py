from django.http import Http404
from django.core.exceptions import PermissionDenied
import nose.tools as nt
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import ProfileFactory
from tests.factories.ticketing_factories import BrownPaperEventsFactory
from tests.functions.gbe_functions import location
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from ticketing.views import bptevent_edit
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestEditBPTEvent(TestCase):
    '''Tests for bptevent_edit view'''

    def setUp(self):
        self.client = Client()
        self.bpt_event = BrownPaperEventsFactory.create()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        self.factory = RequestFactory()

    def get_bptevent_form(self):
        return {
                'title': "Title",
                'description': 'Description',
                'display_icon': 'fa display-icon',
                'primary': True,
                'act_submission_event': True,
                'vendor_submission_event': True,
                'linked_events': [],
                'include_conference': True,
                'include_most': True,
                'badgeable': True,
                'ticket_style': 'ticket style',
                'conference': self.bpt_event.conference.pk
        }

    def test_edit_event_user_is_not_ticketing(self):
        '''
            The user does not have the right privileges.  Send PermissionDenied
        '''
        user = ProfileFactory.create().user_object
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(user, self)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    @nt.raises(Http404)
    def test_edit_event_bad_bptevent(self):
        '''
           Unknown event submitted by valid user, should have an error
           and resend same form (status 200)
        '''
        request = self.factory.get(
            reverse('bptevent_edit',
                    urlconf='ticketing.urls',
                    args=['200']))
        request.user = self.privileged_user
        response = bptevent_edit(request, 200)

    def test_edit_event_good_with_get(self):
        '''
           Good form, good user, get request
        '''
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Ticketing')

    def test_event_edit_post_form_all_good(self):
        '''
            Good form, good user, return the main edit page
        '''
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.get_bptevent_form())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(location(response), '/ticketing/ticket_items')

    def test_event_edit_post_form_bad_event(self):
        '''
            Invalid form data submitted, fail with error and return form
        '''
        error_form = self.get_bptevent_form()
        error_form['linked_events'] = -1
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=error_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Ticketing')
        self.assertContains(response, error_form.get('ticket_style'))
