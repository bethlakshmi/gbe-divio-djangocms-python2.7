from django.http import Http404
from django.core.exceptions import PermissionDenied
import nose.tools as nt
from django.contrib.auth.models import Group
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import bptevent_edit
from tests.factories import gbe_factories, ticketing_factories
from tests.functions.gbe_functions import location
from django.core.urlresolvers import reverse


class TestEditBPTEvent(TestCase):
    '''Tests for bptevent_edit view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.bpt_event = ticketing_factories.BrownPaperEventsFactory.create()
        group, created = Group.objects.get_or_create(name='Ticketing - Admin')
        self.privileged_user = gbe_factories.ProfileFactory.create().\
            user_object
        self.privileged_user.groups.add(group)

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

    @nt.raises(PermissionDenied)
    def test_edit_event_user_is_not_ticketing(self):
        '''
            The user does not have the right privileges.  Send PermissionDenied
        '''
        user = gbe_factories.ProfileFactory.create().user_object
        request = self.factory.get(
            reverse('bptevent_edit',
                    urlconf='ticketing.urls',
                    args=[self.bpt_event.pk]))
        request.user = user
        response = bptevent_edit(request, self.bpt_event.pk)

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
        request = self.factory.get(
            reverse('bptevent_edit',
                    urlconf='ticketing.urls',
                    args=[self.bpt_event.pk]))
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = bptevent_edit(request, self.bpt_event.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Ticketing' in response.content)

    def test_event_edit_post_form_all_good(self):
        '''
            Good form, good user, return the main edit page
        '''
        request = self.factory.post(
            reverse('bptevent_edit',
                    urlconf='ticketing.urls',
                    args=[self.bpt_event.pk]),
            self.get_bptevent_form())
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = bptevent_edit(request, self.bpt_event.pk)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/ticketing/ticket_items')

    def test_event_edit_post_form_bad_event(self):
        '''
            Invalid form data submitted, fail with error and return form
        '''
        error_form = self.get_bptevent_form()
        error_form['linked_events'] = -1
        request = self.factory.post(
            reverse('bptevent_edit',
                    urlconf='ticketing.urls',
                    args=[self.bpt_event.pk]),
            error_form)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = bptevent_edit(request, self.bpt_event.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Ticketing' in response.content)
        nt.assert_true(error_form.get('ticket_style') in response.content)
