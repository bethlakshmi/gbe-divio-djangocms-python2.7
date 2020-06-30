from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import ProfileFactory
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbetext import (
    delete_ticket_fail_message,
    delete_ticket_success_message,
)
from tests.factories.ticketing_factories import (
    TicketItemFactory,
    TransactionFactory,
)


class TestEditTicketItem(TestCase):
    '''Tests for ticket_item_edit view'''
    view_name = 'ticket_item_edit'

    def setUp(self):
        self.client = Client()
        self.ticketitem = TicketItemFactory.create()
        self.privileged_user = ProfileFactory.create().\
            user_object
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        self.url = reverse(
            self.view_name,
            args=[self.ticketitem.pk],
            urlconf='ticketing.urls')

    def get_ticketitem_form(self):
        return {
                'ticket_id': self.ticketitem.ticket_id,
                'title': "Title from Form",
                'live': False,
                'cost': 1.01,
                'bpt_event': self.ticketitem.bpt_event.pk
        }

    def test_edit_ticket_user_is_not_ticketing(self):
        '''
            The user does not have the right privileges.  Send PermissionDenied
        '''
        user = ProfileFactory.create().user_object
        login_as(user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_edit_ticket_bad_ticketitem(self):
        '''
           Unknown ticket item submitted by valid user, should have an error
           and resend same form (status 200)
        '''
        login_as(self.privileged_user, self)
        response = self.client.get(reverse(
            self.view_name,
            args=[200],
            urlconf='ticketing.urls'), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_get_new_ticketitem(self):
        '''
           good user gets new ticket form, all is good.
        '''
        login_as(self.privileged_user, self)
        response = self.client.get("%s?bpt_event_id=%s" % (
            reverse(self.view_name, urlconf='ticketing.urls'),
            self.ticketitem.bpt_event.bpt_event_id))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Ticket Item')
        print(response.content)
        self.assertContains(response, '<option value="%s" selected>' % (
            self.ticketitem.bpt_event.id))

    def test_edit_ticketitem(self):
        '''
           good user gets form to edit existing ticket, all is good.
        '''
        self.ticketitem.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Ticket Item')

    def test_ticket_edit_post_form_and_make_more(self):
        '''
            Good form, good user, return the main edit page
        '''
        login_as(self.privileged_user, self)
        data = self.get_ticketitem_form()
        data['submit_another'] = True
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            "%s?bpt_event_id=%s&updated_tickets=%s&updated_events=[]" % (
                reverse('ticket_item_edit', urlconf='ticketing.urls'),
                self.ticketitem.bpt_event.bpt_event_id,
                str([self.ticketitem.id])))

    def test_ticket_create_post_form_all_good(self):
        '''
            Good form, good user, return the main edit page
        '''
        self.url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        data = self.get_ticketitem_form()
        data['ticket_id'] = "333333-4444444"
        response = self.client.post(self.url, data=data, follow=True)
        self.assertRedirects(
            response,
            ('%s?conference=%s&open_panel=ticket&updated_tickets=%s' +
             '&updated_events=[]') % (
             reverse('ticket_items', urlconf='ticketing.urls'),
             str(self.ticketitem.bpt_event.conference.conference_slug),
             str([self.ticketitem.id+1])))

    def test_ticket_edit_post_form_bad_bptevent(self):
        '''
            Invalid form data submitted, fail with error and return form
        '''
        error_form = self.get_ticketitem_form()
        error_form['bpt_event'] = -1
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data=error_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Ticket Item')
        self.assertContains(response, error_form.get('title'))

    def test_ticket_form_delete(self):
        '''
            Good form, good user, delete item and return to main page
        '''
        login_as(self.privileged_user, self)
        response = self.client.get("%s?delete_item=True" % self.url,
                                   follow=True)
        self.assertRedirects(
            response,
            '%s?conference=%s&open_panel=ticket&updated_events=%s' % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.ticketitem.bpt_event.conference.conference_slug),
                str([self.ticketitem.bpt_event.id])))
        self.assertContains(
            response, 
            delete_ticket_success_message)

    def test_ticket_form_delete_missing_item(self):
        '''
            Good form, good user, delete item that doesn't exist - get an error
        '''
        self.url = reverse(
            self.view_name,
            args=[self.ticketitem.pk+1],
            urlconf='ticketing.urls')
        delete_ticket = self.get_ticketitem_form()
        delete_ticket['delete_item'] = ''
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data=delete_ticket,
            follow=True)
        self.assertEqual(response.status_code, 404)

    def test_delete_ticket_with_transactions(self):
        '''
            Attempt to delete a ticket item that has a transaction
            Get a failure, return to edit page
        '''
        delete_ticket = self.get_ticketitem_form()
        delete_ticket['title'] = "Delete Title"
        delete_ticket['delete_item'] = ''
        transaction = TransactionFactory(ticket_item=self.ticketitem)
        transaction.save()
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data=delete_ticket,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Ticket Item')
        self.assertContains(response, delete_ticket_fail_message)
        self.assertContains(response, self.ticketitem.title)
