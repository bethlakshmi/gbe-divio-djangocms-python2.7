from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import ProfileFactory
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    TransactionFactory,
)
from tests.functions.gbe_functions import location
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from ticketing.views import bptevent_edit
from ticketing.models import BrownPaperEvents
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbetext import (
    delete_event_fail_message,
    delete_event_success_message,
    edit_event_message,
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
                'vendor_submission_event': False,
                'linked_events': [],
                'include_conference': True,
                'include_most': True,
                'badgeable': True,
                'ticket_style': 'ticket style',
                'conference': self.bpt_event.conference.pk,
                'bpt_event_id': self.bpt_event.bpt_event_id,
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

    def test_edit_event_bad_bptevent(self):
        '''
           Unknown event submitted by valid user, should have an error
           and resend same form (status 200)
        '''
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk+1])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_edit_event_good_with_get(self):
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Ticketed Event')

    def test_create_event(self):
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Ticketed Event')

    def test_delete_event(self):
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(self.privileged_user, self)
        response = self.client.get("%s?delete_item=True" % url, follow=True)
        print(response)
        self.assertRedirects(
            response,
            "%s?conference=%s&open_panel=ticket&updated_events=[None]" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.bpt_event.conference.conference_slug)))
        self.assertFalse(BrownPaperEvents.objects.filter(
            id=self.bpt_event.id).exists())
        self.assertContains(response, delete_event_success_message)

    def test_event_edit_post_form_change_to_act_fee(self):
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data=self.get_bptevent_form(),
                                    follow=True)
        self.assertRedirects(
            response,
            "%s?conference=%s&open_panel=act&updated_events=%s" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.bpt_event.conference.conference_slug),
                str([self.bpt_event.id])))

    def test_event_edit_post_form_change_to_vendor_fee(self):
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(self.privileged_user, self)
        data = self.get_bptevent_form()
        data['act_submission_event'] = False
        data['vendor_submission_event'] = True
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertRedirects(
            response,
            "%s?conference=%s&open_panel=vendor&updated_events=%s" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.bpt_event.conference.conference_slug),
                str([self.bpt_event.id])))

    def test_event_edit_post_form_stay_ticket(self):
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(self.privileged_user, self)
        data = self.get_bptevent_form()
        data['act_submission_event'] = False
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertRedirects(
            response,
            "%s?conference=%s&open_panel=ticket&updated_events=%s" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.bpt_event.conference.conference_slug),
                str([self.bpt_event.id])))
        self.assertContains(response, edit_event_message)

    def test_event_edit_post_delete_event_fail(self):
        transaction = TransactionFactory(ticket_item__bpt_event=self.bpt_event)
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(self.privileged_user, self)
        data = self.get_bptevent_form()
        data['delete_item'] = True
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertContains(response, "Edit Ticketed Event")
        self.assertContains(response, delete_event_fail_message)

    def test_event_edit_post_form_make_tickets(self):
        url = reverse('bptevent_edit',
                      urlconf='ticketing.urls',
                      args=[self.bpt_event.pk])
        login_as(self.privileged_user, self)
        data = self.get_bptevent_form()
        data['submit_another'] = True
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertRedirects(
            response,
            "%s?bpt_event_id=%s&updated_events=%s" % (
                reverse('ticket_item_edit', urlconf='ticketing.urls'),
                self.bpt_event.bpt_event_id,
                str([self.bpt_event.id])))
        self.assertContains(response, edit_event_message)

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
        self.assertContains(response, 'Edit Ticketed Event')
        self.assertContains(response, error_form.get('ticket_style'))
